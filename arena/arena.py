import os
import sys
import asyncio
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
                host = "arena.andrew.cmu.edu",
                realm = "realm",
                scene = "render",
                port = None,
                on_msg_callback = None,
                new_obj_callback = None,
                delete_obj_callback = None,
                debug = False,
                network_loop_interval = 10,  # run mqtt client network loop every 10ms
                network_latency_interval = 10000  # run network latency update every 10s
            ):
        if os.environ.get('MQTTH') and os.environ.get('REALM') and os.environ.get('SCENE'):
            self.HOST  = os.environ["MQTTH"]
            self.REALM = os.environ["REALM"]
            self.SCENE = os.environ["SCENE"]
        else:
            print("Cannot find MQTTH, REALM, and SCENE environmental variables, using input parameters instead.")
            if host and realm and scene:
                self.HOST  = host
                self.REALM = realm
                self.SCENE = scene
            else:
                sys.exit("host, realm, and scene are unspecified, aborting...")

        print(f"Loading: {self.HOST}/{self.SCENE}, realm={self.REALM}")
        print("=====")

        self.debug = debug

        self.root_topic = f"{self.REALM}/s/{self.SCENE}"
        self.mqttc_id = "pyClient-" + self.generate_client_id()
        self.latency_topic = "$NETWORK/latency"

        self.mqttc = mqtt.Client(
            self.mqttc_id, clean_session=True
        )

        # do auth
        data = auth.authenticate(self.REALM, self.SCENE, self.HOST, debug=self.debug)
        if 'username' in data and 'token' in data:
            self.mqttc.username_pw_set(username=data["username"], password=data["token"])
        print("=====")

        self.on_msg_callback = on_msg_callback
        self.new_obj_callback = new_obj_callback
        self.delete_obj_callback = delete_obj_callback
        self.secondary_callbacks = {}

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

        if port is not None:
            self.mqttc.connect(self.HOST, port)
        else:
            self.mqttc.connect(self.HOST)

        self.mqttc.subscribe(self.root_topic + "/#")

        # set callbacks
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

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
        print("Connecting to ARENA...")
        self.task_manager.run()

    async def sleep(self, interval_ms):
        """Public function for sleeping in async functions"""
        await asyncio.sleep(interval_ms / 1000)

    def disconnect(self):
        """Disconnects Paho MQTT client"""
        self.mqttc.disconnect()
        print("Disconnected from ARENA!")

    def on_connect(self, client, userdata, flags, rc):
        """Paho MQTT client on_connect callback"""
        if rc == 0:
            self.mqtt_connect_evt.set()
            print("Connected!")
            print("=====")
        else:
            print("Connection error! Result code: " + rc)

    def on_message(self, client, userdata, msg):
        """Paho MQTT client on_message callback"""
        self.process_message(msg)

    def process_message(self, msg):
        """Main message processing function"""

        # check for custom topic
        for sub in self.secondary_callbacks:
            if mqtt.topic_matches_sub(sub, msg.topic):
                self.secondary_callbacks[sub](msg)
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

    def manipulate_camera(self, obj, type="camera-override", **kwargs):
        """Publishes a camera manipulation event"""
        _type = type
        if "target" in kwargs:
            target = kwargs["target"]
            if isinstance(target, tuple) or isinstance(target, list):
                kwargs["target"] = Position(*target)
            elif isinstance(target, dict):
                kwargs["target"] = Position(**target)
            elif isinstance(target, Object):
                kwargs["target"] = target.object_id
        evt = Event(object_id=obj.object_id,
                    type=_type,
                    object_type="camera",
                    **kwargs)
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
        topic = self.root_topic + "/" + obj["object_id"]
        d = datetime.now().isoformat()[:-3]+"Z"
        if action == "delete":
            payload = obj
            payload["action"] = "delete"
            payload["timestamp"] = d
            payload = json.dumps(payload)
        else:
            payload = obj.json(action=action, timestamp=d)

        self.mqttc.publish(topic, payload, qos=0)
        if self.debug: print("[publish]", payload)
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

    def add_topic(self, sub, callback):
        """Subscribes to new topic and adds filter for callback to on_message()"""
        self.secondary_callbacks[sub] = callback
        self.mqttc.subscribe(sub)

    def remove_topic(self, sub):
        """Unsubscribes to topic and removes filter for callback"""
        self.mqttc.unsubscribe(sub)
