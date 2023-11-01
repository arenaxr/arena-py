import argparse
import asyncio
import json
import os
import random
import socket
import ssl
import sys
from datetime import datetime
import threading

import paho.mqtt.client as mqtt

from .auth import ArenaAuth
from .event_loop import *
from .utils import ArenaCmdInterpreter

class ArenaMQTT(object):
    """
    Wrapper around Paho MQTT client and EventLoop.
    """

    scene = None
    device = None
    auth = None

    def __init__(
                self,
                web_host = "arenaxr.org",
                realm = "realm",
                network_latency_interval = 10000,  # run network latency update every 10s
                on_msg_callback = None,
                end_program_callback = None,
                video = False,
                debug = False,
                **kwargs
            ):
        if os.environ.get("MQTTH"):
            self.web_host = os.environ["MQTTH"]
            print(f"Using Host from 'MQTTH' env variable: {self.web_host}")
        elif "host" in kwargs and kwargs["host"]:
            self.web_host = kwargs["host"]
            print(f"Using Host from 'host' input parameter: {self.web_host}")
        else:
            # Use default "web_host", helps avoid and web vs mqtt host and other user setup confusion
            self.web_host = web_host

        if os.environ.get("REALM"):
            self.realm = os.environ["REALM"]
            print(f"Using Realm from 'REALM' env variable: {self.realm}")
        elif "realm" in kwargs and kwargs["realm"]:
            self.realm = kwargs["realm"]
            print(f"Using Realm from 'realm' input parameter: {self.realm}")
        else:
            # Use default "realm" until multiple realms exist, avoids user confusion.
            self.realm = realm

        self.debug = debug

        print("=====")
        # do user auth
        self.username = None
        token = None
        self.remote_auth_token = {}  # provide reference for downloaded token
        self.auth = ArenaAuth()
        if os.environ.get("ARENA_USERNAME") and os.environ.get("ARENA_PASSWORD"):
            # auth 1st: use passed in env var
            self.username = os.environ["ARENA_USERNAME"]
            token = os.environ["ARENA_PASSWORD"]
            self.auth.store_environment_auth(self.username, token)
        else:
            if self.scene:
                local = self.auth.check_local_auth()
            elif self.device:
                local = self.auth.authenticate_device(self.web_host)
            if local and "username" in local and "token" in local:
                # auth 2nd: use locally saved token
                self.username = local["username"]
                token = local["token"]
            else:
                if self.scene:
                    # auth 3rd: use the user account online
                    self.username = self.auth.authenticate_user(self.web_host)

        if os.environ.get("NAMESPACE"):
            self.namespace = os.environ["NAMESPACE"]
        elif "namespace" not in kwargs or ("namespace" in kwargs and kwargs["namespace"] is None):
            self.namespace = self.username
        else:
            self.namespace = kwargs["namespace"]

        # Always use the the hostname specified by the user, or defaults.
        self.mqttc_id = "pyClient-" + self.generate_client_id()

        # fetch host config
        print("Fetching ARENA configuration...")
        self.config_url = f"https://{self.web_host}/conf/defaults.json"
        self.config_data = json.loads(self.auth.urlopen(self.config_url))

        self.mqtt_host = self.config_data["ARENADefaults"]["mqttHost"]

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
            data = self.auth.authenticate_scene(
                self.web_host, self.realm, self.namespaced_target, self.username, video)
            if "username" in data and "token" in data:
                self.username = data["username"]
                token = data["token"]
                self.remote_auth_token = data

        # check for valid permissions to write to the topic
        self.can_publish = self.auth.has_publish_rights(token, self.root_topic)

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
        self.mqttc.on_publish = self.on_publish

        # setup msg counters
        self.msg_io = { 'last_rcv_time': None, 'last_pub_time': None, 'rcv_msgs': 0, 'pub_msgs': 0, 'rcv_msgs_per_sec': 0.0, 'pub_msgs_per_sec': 0.0}
        self.msg_rate_time_start = datetime.now()

        # add main message processing + callbacks loop to tasks
        self.run_async(self.process_message)

        # update network latency every network_latency_interval secs
        self.run_forever(self.network_latency_update,
                         interval_ms=network_latency_interval)

        # update message rate every second
        self.run_forever(self.msg_rate_update,
                         interval_ms=1000)

        self.msg_queue = asyncio.Queue()

        # setup event to let others wait on connection
        self.connected_evt = threading.Event()

        # connect to mqtt broker
        if "port" in kwargs:
            port = kwargs["port"]
        else:
            port = 8883 # ARENA broker TLS 1.2 connection port
        if self.auth.verify(self.web_host):
            self.mqttc.tls_set()
        else:
            self.mqttc.tls_set_context(ssl._create_unverified_context())
            self.mqttc.tls_insecure_set(True)
        try:
            self.mqttc.connect(self.mqtt_host, port=port, keepalive=60)
        except Exception as err:
            print(f'MQTT connect error to {self.mqtt_host}, port={port}: Result Code={err}')
        self.mqttc.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        # check if we want to start the command interpreter
        enable_interp = os.getenv("ENABLE_INTERPRETER", 'False').lower() in ('true', '1', 't')
        if enable_interp:
            self.cmd_interpreter = ArenaCmdInterpreter(self,
                                                       show_attrs=('config_data', 'scene', 'users', 'all_objects', 'msg_io'),
                                                       get_callables=('persisted_objs', 'persisted_scene_option', 'writable_scenes', 'user_list'))
            self.cmd_interpreter.start_thread(self.connected_evt)


    def parse_cli(self):
        """
        Reusable command-line options to give apps flexible options to avoid hard-coding locations.
        """
        parser = argparse.ArgumentParser(description=("arena-py Application CLI"))
        parser.add_argument("-mh", "--host", type=str,
                            help="ARENA webserver main host to connect to")
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
        parser.add_argument("-c", "--scale", nargs=3, type=float, default=(1, 1, 1),
                            help="App scale in meters")
        parser.add_argument("-D", "--debug", action='store_true', help='Debug mode.', default=False)
        args = parser.parse_args()
        app_position = tuple(args.position)
        app_rotation = tuple(args.rotation)
        app_scale = tuple(args.scale)
        return {
            "host": args.host,
            "namespace": args.namespace,
            "scene": args.scene,
            "device": args.device,
            "position": app_position,
            "rotation": app_rotation,
            "scale": app_scale,
            "debug": args.debug,
        }

    def generate_client_id(self):
        """Returns a random 6 digit id"""
        return str(random.randrange(100000, 999999))

    def network_latency_update(self):
        """Update client latency in $NETWORK/latency"""
        # publish empty message with QoS of 2 to update latency
        self.mqttc.publish(self.latency_topic, "", qos=2)

    def msg_rate_update(self):
        """Update Message rate"""
        elapsed = datetime.now() - self.msg_rate_time_start
        if elapsed.seconds > 0:
            self.msg_io['rcv_msgs_per_sec'] = round(self.msg_io['rcv_msgs']  / elapsed.seconds, 2)
            self.msg_io['pub_msgs_per_sec'] = round(self.msg_io['pub_msgs']  / elapsed.seconds, 2)

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
        print("Connecting to the ARENA... ", end="", flush=True)
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

            # set event
            self.connected_evt.set()

            # reset msg rate time
            self.msg_rate_time_start = datetime.now()

            print("Connected!")
            print("=====")

        else:
            print(f"Connection error! Result code={rc}")

    def on_message(self, client, userdata, msg):
        # ignore own messages
        if mqtt.topic_matches_sub(self.ignore_topic, msg.topic):
            return
        self.msg_io['last_rcv_time'] = datetime.now()
        self.msg_io['rcv_msgs'] = self.msg_io['rcv_msgs'] + 1
        self.msg_queue.put_nowait(msg)

    async def process_message(self):
        raise NotImplementedError("Must override process_message")

    def on_disconnect(self, client, userdata, rc):
        """Paho MQTT client on_disconnect callback"""
        if rc == 0:
            print("Disconnected from the ARENA!")
        else:
            print(f"Disconnected! Result code={rc}.")

    def disconnect(self):
        """Disconnects Paho MQTT client"""
        if self.end_program_callback:
            self.end_program_callback(self)
        self.mqttc.disconnect()

    def on_publish(self, client, userdata, mid):
        self.msg_io['last_pub_time'] = datetime.now()
        self.msg_io['pub_msgs'] = self.msg_io['pub_msgs'] + 1

    def message_callback_add(self, sub, callback):
        """Subscribes to new topic and adds callback"""
        self.mqttc.subscribe(sub)
        self.mqttc.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        """Unsubscribes to topic and removes callback"""
        self.mqttc.unsubscribe(sub)
        self.mqttc.message_callback_remove(sub)
