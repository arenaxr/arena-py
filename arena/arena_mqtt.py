import asyncio
import json
import os
import random
import socket
import sys
from datetime import datetime

from .auth import ArenaAuth
from .env import ARENA_PASSWORD, ARENA_USERNAME, MQTTH, NAMESPACE, REALM, _get_env
from .event_loop import *
from .paho.mqtt import client as mqtt
from .topics import PUBLISH_TOPICS, SUBSCRIBE_TOPICS, TOPIC_TYPES

try:
    import ssl
except ImportError:
    ssl = None

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
                headless = False,
                environment = False,
                **kwargs
            ):
        if os.environ.get(MQTTH):
            self.web_host = _get_env(MQTTH)
            print(f"Using Host from 'MQTTH' env variable: {self.web_host}")
        elif "host" in kwargs and kwargs["host"]:
            self.web_host = kwargs["host"]
            print(f"Using Host from 'host' input parameter: {self.web_host}")
        else:
            # Use default "web_host", helps avoid and web vs mqtt host and other user setup confusion
            self.web_host = web_host

        if os.environ.get(REALM):
            self.realm = _get_env(REALM)
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
        if os.environ.get(ARENA_USERNAME) and os.environ.get(ARENA_PASSWORD):
            # auth 1st: use passed in env var
            self.username = _get_env(ARENA_USERNAME)
            token = _get_env(ARENA_PASSWORD)
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
                    self.username = self.auth.authenticate_user(self.web_host, headless)

        if os.environ.get(NAMESPACE):
            self.namespace = _get_env(NAMESPACE)
        elif "namespace" not in kwargs or ("namespace" in kwargs and kwargs["namespace"] is None):
            self.namespace = self.username
        else:
            self.namespace = kwargs["namespace"]

        if self.scene:
            self.namespaced_target = f"{self.namespace}/{self.scene}"
        elif self.device:
            self.namespaced_target = f"{self.namespace}/{self.device}"

        # Always use the the hostname specified by the user, or defaults.
        self.mqttc_id = "pyClient-" + self.generate_client_id()

        # fetch host config
        print("Fetching ARENA configuration...")
        self.config_url = f"https://{self.web_host}/conf/defaults.json"
        self.config_data = json.loads(self.auth.urlopen(self.config_url))

        self.mqtt_host = self.config_data["ARENADefaults"]["mqttHost"]

        if self.scene and (not self.username or not token):
            # do scene auth by user
            data = self.auth.authenticate_scene(
                self.web_host, self.realm, self.namespaced_target, self.username, video, environment
            )
            if "username" in data and "token" in data and "ids" in data:
                self.username = data["username"]
                token = data["token"]
                self.remote_auth_token = data

        # prefer user_id from account, however root tokens use mqtt client_id as a substitute
        if self.remote_auth_token and "ids" in self.remote_auth_token and "userid" in self.remote_auth_token["ids"]:
            self.userid = self.remote_auth_token["ids"]["userid"]
            self.userclient = self.remote_auth_token["ids"]["userclient"]
        else:
            self.userid = self.mqttc_id
            self.userclient = self.mqttc_id

        # set up topic variables
        self.topicParams = {  # Reusable topic param dict
            "realm": self.realm,
            "nameSpace": self.namespace,
            # adding "sceneName" or "deviceName" depending on case below
            "userClient": self.userclient,
            "idTag": self.userid,
        }
        if self.scene:
            self.topicParams["sceneName"] = self.scene
            self.subscribe_topics = {
                'public': SUBSCRIBE_TOPICS.SCENE_PUBLIC.substitute(self.topicParams),
                'private': SUBSCRIBE_TOPICS.SCENE_PRIVATE.substitute(self.topicParams)
            }
            if environment:
                self.subscribe_topics["envhost"] = SUBSCRIBE_TOPICS.SCENE_ENV_PRIVATE.substitute(
                    {**self.topicParams, **{"idTag": "-"}}
                )
        elif self.device:
            self.topicParams["deviceName"] = self.device
            self.subscribe_topics = {
                'public': SUBSCRIBE_TOPICS.DEVICE.substitute(self.topicParams),
            }
        self.latency_topic = self.config_data["ARENADefaults"]["latencyTopic"]  # network graph latency update
        self.ignore_topic = SUBSCRIBE_TOPICS.SCENE_PUBLIC_SELF.substitute(self.topicParams)

        # check for valid permissions to write to all objects topics
        self.can_publish_obj = self.auth.has_publish_rights(
            token,
            PUBLISH_TOPICS.SCENE_OBJECTS.substitute({**self.topicParams, **{"objectId": "anyfoobject"}})
        )

        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, self.mqttc_id, clean_session=True
        )
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
        self.subscriptions = {}
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe

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
            port = 8883  # ARENA broker TLS 1.2 connection port
        if self.auth.verify(self.web_host):
            self.mqttc.tls_set(tls_version=ssl.PROTOCOL_TLS)
        else:
            self.mqttc.tls_set_context(ssl._create_unverified_context())
            self.mqttc.tls_insecure_set(True)
        try:
            self.mqttc.connect(self.mqtt_host, port=port, keepalive=60)
        except Exception as err:
            print(f'MQTT connect error to {self.mqtt_host}, port={port}: Result Code={err}')
        self.mqttc.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

    def generate_client_id(self):
        """Returns a random 6 digit id."""
        return str(random.randrange(100000, 999999))

    def network_latency_update(self):
        """Update client latency in $NETWORK/latency."""
        # publish empty message with QoS of 2 to update latency
        self.mqttc.publish(self.latency_topic, "", qos=2)

    def run_once(self, func=None, **kwargs):
        """Runs a user-defined function on startup."""
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
        """Runs a user-defined function after a interval_ms milliseconds."""
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
        """Runs a user defined aynscio function."""
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
        """Runs a function every interval_ms milliseconds."""
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
        """Run event loop."""
        print("Connecting to the ARENA...")
        self.event_loop.run()

    def stop_tasks(self):
        """Stop event loop."""
        self.event_loop.stop()

    async def sleep(self, interval_ms):
        """Public function for sleeping in async functions."""
        await asyncio.sleep(interval_ms / 1000)

    def on_connect(self, client, userdata, flags, rc, properties):
        """Paho MQTT client on_connect callback."""
        if rc == 0:
            self.mqtt_connect_evt.set()

            # listen to all messages in scene
            self.do_subscribe(client, self.subscribe_topics['public'], self.on_message)
            if self.subscribe_topics.get('private'):
                self.do_subscribe(client, self.subscribe_topics['private'], self.on_message_private)

            # reset msg rate time
            self.msg_rate_time_start = datetime.now()

            print("Connected!")
            print("=====")

        else:
            print(f"Connection error! Result code={rc}")
            os._exit(1)

    def do_subscribe(self, client, topic, callback):
        result, mid = client.subscribe(topic)
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.subscriptions[mid] = topic
        else:
            print(f"Subscribe ERROR!!! topic={topic} result code={result}")
        client.message_callback_add(topic, callback)

    def on_message(self, client, userdata, msg):
        # ignore own messages
        if mqtt.topic_matches_sub(self.ignore_topic, msg.topic):
            return
        self.msg_queue.put_nowait(msg)

    def on_message_private(self, client, userdata, msg):
        # Private messages are never reflected to self, no check required
        self.msg_queue.put_nowait(msg)

    async def process_message(self):
        raise NotImplementedError("Must override process_message")

    def on_subscribe(self, client, userdata, mid, rc_list, properties):
        if self.debug:
            print(f"[subscribe ack]: topic={self.subscriptions[mid]} rc_list={rc_list}")
        for rc in rc_list:
            if rc >= 128:
                # Any reason code >= 128 is a failure.
                if mid in self.subscriptions:
                    print(f"FAILURE!!! Subscribing to topic {self.subscriptions[mid]}")
                else:
                    print(f"FAILURE!!! Subscribing to topic with message id: {mid}")

    def on_disconnect(self, client, userdata, rc, properties):
        """Paho MQTT client on_disconnect callback."""
        if rc == 0:
            print("Disconnected from the ARENA!")
        else:
            print(f"Disconnected! Result code={rc}.")

        os._exit(rc)

    def disconnect(self):
        """Disconnects Paho MQTT client."""
        if self.end_program_callback:
            self.end_program_callback(self)
        self.mqttc.disconnect()

    def message_callback_add(self, sub, callback):
        """Subscribes to new topic and adds callback."""
        self.do_subscribe(self.mqttc, sub, callback)

    def message_callback_remove(self, sub):
        """Unsubscribes to topic and removes callback."""
        self.mqttc.unsubscribe(sub)
        self.mqttc.message_callback_remove(sub)

    def rcv_queue_len(self):
        """Return receive queue length."""
        self.msg_queue.qsize()

    def pub_queue_len(self):
        """Return publish queue length."""
        return self.mqttc._out_packet

    def client_id(self):
        """Return client id."""
        return self.mqttc_id
