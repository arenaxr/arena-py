import argparse
import asyncio
import json
import os
import random
import socket
import sys
import urllib.request

import paho.mqtt.client as mqtt

from . import auth
from .event_loop import *


class ArenaMQTT(object):
    """
    Wrapper around Paho MQTT client and EventLoop.
    """

    scene = None
    device = None

    def __init__(
                self,
                realm = "realm",
                network_latency_interval = 10000,  # run network latency update every 10s
                on_msg_callback = None,
                end_program_callback = None,
                video = False,
                debug = False,
                cli_args = False,
                **kwargs
            ):
        if cli_args:
            self.args = self.parse_cli()
            if self.args["mqtth"]:
                kwargs["host"] = self.args["mqtth"]
            if self.args["namespace"]:
                kwargs["namespace"] = self.args["namespace"]
            if self.args["scene"]:
                kwargs["scene"] = self.args["scene"]
            if self.args["device"]:
                kwargs["device"] = self.args["device"]

        if os.environ.get("MQTTH"):
            self.host = os.environ["MQTTH"]
        elif "host" in kwargs and kwargs["host"]:
            self.host = kwargs["host"]
            print("Cannot find MQTTH environmental variable, using input parameter instead.")
        else:
            sys.exit("mqtt host argument (host) is unspecified or None, aborting...")

        if os.environ.get("REALM"):
            self.realm = os.environ["REALM"]
        elif "realm" in kwargs and kwargs["realm"]:
            self.realm = kwargs["realm"]
            print("Cannot find REALM environmental variable, using input parameter instead.")
        else:
            # Use default "realm" until multiple realms exist, avoids user confusion.
            self.realm = realm

        self.debug = debug

        print("=====")
        # do user auth
        self.username = None
        token = None
        self.remote_auth_token = {}  # provide reference for downloaded token
        if os.environ.get("ARENA_USERNAME") and os.environ.get("ARENA_PASSWORD"):
            # auth 1st: use passed in env var
            self.username = os.environ["ARENA_USERNAME"]
            token = os.environ["ARENA_PASSWORD"]
            auth.store_environment_auth(self.username, token)
        else:
            if self.scene:
                local = auth.check_local_auth()
            elif self.device:
                local = auth.authenticate_device(self.host)
            if local and "username" in local and "token" in local:
                # auth 2nd: use locally saved token
                self.username = local["username"]
                token = local["token"]
            else:
                if self.scene:
                    # auth 3rd: use the user account online
                    self.username = auth.authenticate_user(self.host)

        if os.environ.get("NAMESPACE"):
            self.namespace = os.environ["NAMESPACE"]
        elif "namespace" not in kwargs or ("namespace" in kwargs and kwargs["namespace"] is None):
            self.namespace = self.username
        else:
            self.namespace = kwargs["namespace"]

        self.mqttc_id = "pyClient-" + self.generate_client_id()

        # fetch host config
        print("Fetching ARENA configuration...")
        self.config_url = f"https://{self.host}/conf/defaults.json"
        with urllib.request.urlopen(self.config_url) as url:
            self.config_data = json.loads(url.read().decode())

        # set up topic variables
        if self.scene:
            self.namespaced_target =  f"{self.namespace}/{self.scene}"
            self.root_topic = f"{self.realm}/s/{self.namespaced_target}"
        elif self.device:
            self.namespaced_target =  f"{self.namespace}/{self.device}"
            self.root_topic = f"{self.realm}/d/{self.namespaced_target}"
        self.subscribe_topic = f"{self.root_topic}/#"   # main topic for entire target
        self.latency_topic = self.config_data["ARENADefaults"]["latencyTopic"] # network graph latency update
        self.ignore_topic = f"{self.root_topic}/{self.mqttc_id}/#" # ignore own messages

        self.mqttc = mqtt.Client(
            self.mqttc_id, clean_session=True
        )

        if self.scene and (not self.username or not token):
            # do scene auth by user
            data = auth.authenticate_scene(
                self.host, self.realm, self.namespaced_target, self.username, video)
            if "username" in data and "token" in data:
                self.username = data["username"]
                token = data["token"]
                self.remote_auth_token = data
        self.mqttc.username_pw_set(username=self.username, password=token)
        print("=====")

        # set up callbacks
        self.on_msg_callback = on_msg_callback
        self.end_program_callback = end_program_callback

        self.event_loop = EventLoop(self.disconnect)

        aioh = AsyncioMQTTHelper(self.event_loop, self.mqttc)

        # have all tasks wait until mqtt client is connected before starting
        self.mqtt_connect_evt = asyncio.Event()
        self.mqtt_connect_evt.clear()

        # set paho mqtt callbacks
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect

        # add main message processing + callbacks loop to tasks
        self.run_async(self.process_message)

        # update network latency every network_latency_interval secs
        self.run_forever(self.network_latency_update,
                         interval_ms=network_latency_interval)

        self.msg_queue = asyncio.Queue()

        # connect to mqtt broker
        if "port" in kwargs:
            port = kwargs["port"]
        else:
            port = 8883 # ARENA broker TLS 1.2 connection port
            self.mqttc.tls_set()
        try:
            self.mqttc.connect(self.host, port=port)
        except Exception as err:
            print(f'MQTT connect error to {self.host}, port={port}: {err}')
        self.mqttc.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)


    def parse_cli(self):
        """
        Reusable command-line options to give apps flexible options to avoid hard-coding locations.
        """
        parser = argparse.ArgumentParser(description=("ARENA-py Application CLI"))
        parser.add_argument("-mh", "--mqtth", type=str,
                            help="MQTT host to connect to")
        parser.add_argument("-n", "--namespace", type=str,
                            help="Namespace of scene")
        parser.add_argument("-s", "--scene", type=str,
                            help="Scene to publish and listen to")
        parser.add_argument("-d", "--device", type=str,
                            help="Device to publish and listen to")
        parser.add_argument("-p", "--position", nargs=3, type=float, default=(0, 0, 0),
                            help="App position as cartesian.x cartesian.y cartesian.z")
        parser.add_argument("-r", "--rotation", nargs=3, type=float, default=(0, 0, 0),
                            help="App rotation as euler.x euler.y euler.z")
        args = parser.parse_args()
        app_position = tuple(args.position)
        app_rotation = tuple(args.rotation)
        return {
            "mqtth": args.mqtth,
            "namespace": args.namespace,
            "scene": args.scene,
            "device": args.device,
            "position": app_position,
            "rotation": app_rotation,
        }


    def generate_client_id(self):
        """Returns a random 6 digit id"""
        return str(random.randrange(100000, 999999))

    def network_latency_update(self):
        """Update client latency in $NETWORK/latency"""
        # publish empty message with QoS of 2 to update latency
        self.mqttc.publish(self.latency_topic, "", qos=2)

    def run_once(self, func=None, **kwargs):
        """Runs a user-defined function on startup"""
        if func is not None:
            w = SingleWorker(self.event_loop, func, self.mqtt_connect_evt, **kwargs)
            self.event_loop.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_once(func):
                self.run_once(func, **kwargs)
                return func
            return _run_once

    def run_after_interval(self, func=None, interval_ms=1000, **kwargs):
        """Runs a user-defined function after a interval_ms milliseconds"""
        if func is not None:
            if interval_ms < 0:
                print("Invalid interval! Defaulting to 1000ms")
                interval_ms = 1000
            w = LazyWorker(self.event_loop, func, self.mqtt_connect_evt, interval_ms, **kwargs)
            self.event_loop.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_after_interval(func):
                self.run_after_interval(func, interval_ms, **kwargs)
                return func
            return _run_after_interval

    def run_async(self, func=None, **kwargs):
        """Runs a user defined aynscio function"""
        if func is not None:
            w = AsyncWorker(self.event_loop, func, self.mqtt_connect_evt, **kwargs)
            self.event_loop.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_async(func):
                self.run_async(func, **kwargs)
                return func
            return _run_async

    def run_forever(self, func=None, interval_ms=1000, **kwargs):
        """Runs a function every interval_ms milliseconds"""
        if func is not None:
            if interval_ms < 0:
                print("Invalid interval! Defaulting to 1000ms")
                interval_ms = 1000
            t = PersistentWorker(self.event_loop, func, self.mqtt_connect_evt, interval_ms, **kwargs)
            self.event_loop.add_task(t)
        else:
            # if there is no func, we are in a decorator
            def _run_forever(func):
                self.run_forever(func, interval_ms, **kwargs)
                return func
            return _run_forever

    def run_tasks(self):
        """Run event loop"""
        print("Connecting to the ARENA... ", end="")
        self.event_loop.run()

    def stop_tasks(self):
        """Stop event loop"""
        self.event_loop.stop()

    async def sleep(self, interval_ms):
        """Public function for sleeping in async functions"""
        await asyncio.sleep(interval_ms / 1000)

    def on_connect(self, client, userdata, flags, rc):
        """Paho MQTT client on_connect callback"""
        if rc == 0:
            self.mqtt_connect_evt.set()

            # listen to all messages in scene
            client.subscribe(self.subscribe_topic)
            client.message_callback_add(self.subscribe_topic, self.on_message)

            print("Connected!")
            print("=====")
        else:
            print(f"Connection error! Result code: {rc}")

    def on_message(self, client, userdata, msg):
        # ignore own messages
        if mqtt.topic_matches_sub(self.ignore_topic, msg.topic):
            return

        self.msg_queue.put_nowait(msg)

    async def process_message(self):
        raise NotImplementedError("Must override process_message")

    def on_disconnect(self, client, userdata, rc):
        """Paho MQTT client on_disconnect callback"""
        if rc == 0:
            print("Disconnected from the ARENA!")
        else:
            print(f"Disconnect error! Result code: {rc}")

    def disconnect(self):
        """Disconnects Paho MQTT client"""
        if self.end_program_callback:
            self.end_program_callback(self)
        self.mqttc.disconnect()

    def message_callback_add(self, sub, callback):
        """Subscribes to new topic and adds callback"""
        self.mqttc.subscribe(sub)
        self.mqttc.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        """Unsubscribes to topic and removes callback"""
        self.mqttc.unsubscribe(sub)
        self.mqttc.message_callback_remove(sub)
