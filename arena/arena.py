import os
import sys
import asyncio
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime

from .attributes import *
from .objects import *
from .events import *
from .utils import *
from .event_loop import *

from . import auth

class Arena(object):
    """
    Main ARENA client for ARENA-py.
    Wrapper around Paho MQTT client and EventLoop.
    Can create and execute various user-defined functions.
    """
    def __init__(
                self,
                on_msg_callback = None,
                new_obj_callback = None,
                delete_obj_callback = None,
                debug = False,
                network_loop_interval = 50,  # run mqtt client network loop every 50ms
                network_latency_interval = 10000,  # run network latency update every 10s
                **kwargs
            ):
        if os.environ.get("MQTTH"):
            self.HOST  = os.environ["MQTTH"]
        elif "host" in kwargs:
            self.HOST = kwargs["host"]
            print("Cannot find MQTTH environmental variable, using input parameter instead.")
        else:
            sys.exit("MQTTH (host) is unspecified, aborting...")

        if os.environ.get("REALM"):
            self.REALM  = os.environ["REALM"]
        elif "realm" in kwargs:
            self.REALM = kwargs["realm"]
            print("Cannot find REALM environmental variable, using input parameter instead.")
        else:
            sys.exit("REALM (realm) is unspecified, aborting...")

        if os.environ.get("SCENE"):
            self.SCENE  = os.environ["SCENE"]
        elif "scene" in kwargs:
            self.SCENE = kwargs["scene"]
            print("Cannot find SCENE environmental variable, using input parameter instead.")
        else:
            sys.exit("SCENE (scene) is unspecified, aborting...")

        # do user auth
        username = auth.authenticate_user(self.HOST, debug=debug)
        if "namespace" not in kwargs:
            self.NAMESPACE = username
        else:
            self.NAMESPACE = kwargs["namespace"]

        print(f"Loading: {self.HOST}/{self.NAMESPACE}/{self.SCENE}, realm={self.REALM}")
        print("=====")

        self.debug = debug

        self.mqttc_id = "pyClient-" + self.generate_client_id()

        self.namespace_scene =  f"{self.NAMESPACE}/{self.SCENE}"
        self.root_topic = f"{self.REALM}/s/{self.namespace_scene}"
        self.scene_topic = f"{self.root_topic}/#"   # main topic for entire scene
        self.latency_topic = "$NETWORK/latency"     # network graph latency update
        self.ignore_topic = f"{self.root_topic}/{self.mqttc_id}/#" # ignore own messages

        self.mqttc = mqtt.Client(
            self.mqttc_id, clean_session=True
        )

        # do scene auth
        data = auth.authenticate_scene(self.HOST, self.REALM, self.namespace_scene, username, self.debug)
        if 'username' in data and 'token' in data:
            self.mqttc.username_pw_set(username=data["username"], password=data["token"])
        print("=====")

        self.on_msg_callback = on_msg_callback
        self.new_obj_callback = new_obj_callback
        self.delete_obj_callback = delete_obj_callback

        self.unspecified_objs_ids = set() # objects that exist in scene, but user does not have reference to

        self.task_manager = EventLoop(self.disconnect)

        # have all tasks wait until mqtt client is connected before starting
        self.mqtt_connect_evt = asyncio.Event()
        self.mqtt_connect_evt.clear()

        # add mqtt client loop to list of tasks
        self.network_loop_interval = network_loop_interval
        self.network_loop = PersistantWorker(
                                func=self.run_network_loop,
                                event=None,
                                interval=self.network_loop_interval
                            )
        self.task_manager.add_task(self.network_loop)

        # run network latency update task every 10 secs
        self.run_forever(self.network_latency_update, interval_ms=network_latency_interval)

        if "port" in kwargs:
            self.mqttc.connect(self.HOST, port)
        else:
            self.mqttc.connect(self.HOST)

        # set callbacks
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect

    def generate_client_id(self):
        """Returns a random 6 digit id"""
        return str(random.randrange(100000, 999999))

    def run_network_loop(self):
        """Main Paho MQTT client network loop"""
        self.mqttc.loop()

    def network_latency_update(self):
        """Update client latency in $NETWORK/latency"""
        self.mqttc.publish(self.latency_topic, "", qos=2)

    def run_once(self, func=None, **kwargs):
        """Runs a user-defined function on startup"""
        if func is not None:
            w = SingleWorker(func, self.mqtt_connect_evt, **kwargs)
            self.task_manager.add_task(w)
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
            w = LazyWorker(func, self.mqtt_connect_evt, interval_ms, **kwargs)
            self.task_manager.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_after_interval(func):
                self.run_after_interval(func, interval_ms, **kwargs)
                return func
            return _run_after_interval

    def run_async(self, func=None, **kwargs):
        """Runs a user defined aynscio function"""
        if func is not None:
            w = AsyncWorker(func, self.mqtt_connect_evt, **kwargs)
            self.task_manager.add_task(w)
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
            t = PersistantWorker(func, self.mqtt_connect_evt, interval_ms, **kwargs)
            self.task_manager.add_task(t)
        else:
            # if there is no func, we are in a decorator
            def _run_forever(func):
                self.run_forever(func, interval_ms, **kwargs)
                return func
            return _run_forever

    def run_tasks(self):
        """Run event loop"""
        print("Connecting to the ARENA...")
        self.task_manager.run()

    async def sleep(self, interval_ms):
        """Public function for sleeping in async functions"""
        await asyncio.sleep(interval_ms / 1000)

    def on_connect(self, client, userdata, flags, rc):
        """Paho MQTT client on_connect callback"""
        if rc == 0:
            self.mqtt_connect_evt.set()

            # listen to all messages in scene
            self.mqttc.subscribe(self.scene_topic)
            self.mqttc.message_callback_add(self.scene_topic, self.process_message)

            print("Connected!")
            print("=====")
        else:
            print("Connection error! Result code: " + rc)

    def disconnect(self):
        """Disconnects Paho MQTT client"""
        self.mqttc.disconnect()

    def on_disconnect(self, client, userdata, rc):
        """Paho MQTT client on_disconnect callback"""
        if rc == 0:
            print("Disconnected from the ARENA!")
        else:
            print("Disconnect error! Result code: " + rc)

    def process_message(self, client, userdata, msg):
        """Main message processing function"""
        if mqtt.topic_matches_sub(self.ignore_topic, msg.topic):
            return

        # extract payload
        try:
            payload_str = msg.payload.decode("utf-8", "ignore")
            payload = json.loads(payload_str)
        except:
            return

        # update object attributes, if possible
        if "object_id" in payload:
            # check for events/object updates
            event = None
            if "action" in payload:
                if payload["action"] == "clientEvent":
                    event = Event(**payload)
                elif self.delete_obj_callback and payload["action"] == "delete":
                    self.delete_obj_callback(payload)
                    return

            object_id = payload["object_id"]
            if object_id in self.all_objects:
                obj = self.all_objects[object_id]
                if not event: # update object if not an event
                    obj.update_attributes(**payload)
                elif obj.evt_handler:
                    obj.evt_handler(event)

            # if it is an object the lib has not seen before, call new object callback
            elif object_id not in self.unspecified_objs_ids and self.new_obj_callback:
                self.new_obj_callback(payload)
                self.unspecified_objs_ids.add(object_id)

            # call new message callback if not an event
            if not event and self.on_msg_callback:
                self.on_msg_callback(payload)

    def generate_custom_event(self, evt, action="clientEvent"):
        """Publishes an custom event. Could be user or library defined"""
        return self._publish(evt, action)

    def generate_click_event(self, obj, type="mousedown", **kwargs):
        """Publishes an click event"""
        _type = type
        evt = Event(object_id=obj.object_id,
                    type=_type,
                    position=obj.data.position,
                    source=self.mqttc_id,
                    **kwargs)
        return self.generate_custom_event(evt, action="clientEvent")

    def manipulate_camera(self, cam, **kwargs):
        """Publishes a camera manipulation event"""
        if kwargs["position"] is not None:
            if isinstance(kwargs["position"], tuple) or isinstance(kwargs["position"], list):
                kwargs["position"] = Position(*kwargs["position"])
            elif isinstance(position, dict):
                kwargs["position"] = Position(**kwargs["position"])

        if kwargs["rotation"] is not None:
            if isinstance(kwargs["rotation"], tuple) or isinstance(kwargs["rotation"], list):
                kwargs["rotation"] = Rotation(*kwargs["rotation"])
            elif isinstance(rotation, dict):
                kwargs["rotation"] = Rotation(**kwargs["rotation"])

        if isinstance(cam, Object):
            object_id = cam.object_id
        else:
            object_id = cam
        evt = Event(object_id=object_id,
                    type="camera-override",
                    object_type="camera",
                    **kwargs)
        return self.generate_custom_event(evt, action="create")

    def look_at(self, cam, target):
        """Publishes a camera manipulation event"""
        if isinstance(target, tuple) or isinstance(target, list):
            target = Position(*target)
        elif isinstance(target, dict):
            target = Position(**target)
        elif isinstance(target, Object):
            target = target.object_id

        if isinstance(cam, Object):
            object_id = cam.object_id
        else:
            object_id = cam
        evt = Event(object_id=object_id,
                    type="camera-override",
                    object_type="look-at",
                    target=target)
        return self.generate_custom_event(evt, action="create")

    @property
    def all_objects(self):
        """Returns all objects created by the user"""
        return Object.all_objects

    def add_object(self, obj):
        """Public function to create an object"""
        return self._publish(obj, "create")

    def update_object(self, obj, **kwargs):
        """Public function to update an object"""
        if kwargs:
            obj.update_attributes(**kwargs)
        return self._publish(obj, "update")

    def delete_object(self, obj):
        """Public function to delete an object"""
        payload = {
            "object_id": obj.object_id
        }
        Object.remove(obj)
        return self._publish(payload, "delete")

    def _publish(self, obj, action):
        """Publishes to mqtt broker with "action":action"""
        topic = f"{self.root_topic}/{self.mqttc_id}/{obj['object_id']}"
        d = datetime.now().isoformat()[:-3]+"Z"
        if action == "delete":
            payload = obj
            payload["action"] = "delete"
            payload["timestamp"] = d
            payload = json.dumps(payload)
        else:
            payload = obj.json(action=action, timestamp=d)

        self.mqttc.publish(topic, payload, qos=0)
        if self.debug: print("[publish]", topic, payload)
        return payload

    def get_persisted_obj(self, object_id, broker, scene):
        """Returns a dictionary for a persisted object. [TODO] wrap the output as an Object"""
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}/{object_id}', creds=True)
        output = json.loads(data)
        if self.debug: print("[get_persisted_obj]", output)
        return output

    def get_persisted_scene_option(self, broker, scene):
        """Returns a dictionary for scene-options. [TODO] wrap the output as a BaseObject"""
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}', creds=True)
        output = json.loads(data)
        if self.debug: print("[get_persisted_scene_option]", output)
        return output

    def message_callback_add(self, sub, callback):
        """Subscribes to new topic and adds callback"""
        self.mqttc.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        """Unsubscribes to topic and removes filter for callback"""
        self.mqttc.message_callback_remove(sub)
