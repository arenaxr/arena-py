import os
import sys
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
    Can create and execute various user defined functions.
    """
    def __init__(self,
                host = None,
                scene = None,
                realm = None,
                port = None,
                on_msg_callback = None,
                new_obj_callback = None,
                debug = False,
                webhost = 'xr.andrew.cmu.edu'
            ):
        if os.environ.get('MQTTH') and os.environ.get('SCENE') and os.environ.get('REALM'):
            HOST  = os.environ["MQTTH"]
            SCENE = os.environ["SCENE"]
            REALM = os.environ["REALM"]
        else:
            print("Cannot find SCENE, MQTTH, and REALM environmental variables, using input parameters instead.")
            if host and scene and realm:
                HOST  = host
                SCENE = scene
                REALM = realm
            else:
                sys.exit("scene, host, and realm are unspecified, aborting...")

        print(f"Loading: {HOST}/{SCENE}, realm={REALM}")
        print("=====")

        self.root_topic = f"{REALM}/s/{SCENE}"
        self.client_id = random_client_id()
        self.debug = debug

        self.client = mqtt.Client(
            "pyClient-" + self.client_id, clean_session=True
        )

        # do auth
        data = auth.authenticate(REALM, SCENE, HOST, webhost=webhost,
                                                     debug=self.debug)
        if 'username' in data and 'token' in data:
            self.client.username_pw_set(username=data["username"], password=data["token"])
        print("=====")

        self.on_msg_callback = on_msg_callback
        self.new_obj_callback = new_obj_callback
        self.secondary_callbacks = {}

        self.unspecified_objs_ids = set() # objects that exist in scene, but user does not have reference to
        self.task_manager = EventLoop(self.disconnect)

        # add mqtt client loop to list of tasks
        self.network_loop = PersistantWorker(self.run_network_loop, 0.01)
        self.task_manager.add_task(self.network_loop)

        if port is not None:
            self.client.connect(HOST, port)
        else:
            self.client.connect(HOST)

        self.client.subscribe(self.root_topic + "/#")

        # set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def run_network_loop(self):
        """Main Paho MQTT client network loop"""
        self.client.loop()

    def run_once(self, func=None, *args, **kwargs):
        """Runs a user defined function on startup"""
        if func is not None:
            w = SingleWorker(func, *args, **kwargs)
            self.task_manager.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_once(func):
                self.run_once(func, *args, **kwargs)
                return func
            return _run_once

    def run_after_interval(self, func=None, interval_ms=1000, *args, **kwargs):
        """Runs a user defined function after a interval_ms milliseconds"""
        if func is not None:
            if interval_ms < 0:
                print("Invalid interval! Defaulting to 1000ms")
                interval_ms = 1000
            w = LazyWorker(func, float(interval_ms) / 1000, *args, **kwargs)
            self.task_manager.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_after_interval(func):
                self.run_after_interval(func, interval_ms, *args, **kwargs)
                return func
            return _run_after_interval

    def run_async(self, func=None, *args, **kwargs):
        """Runs a user defined aynscio function"""
        if func is not None:
            w = AsyncWorker(func, *args, **kwargs)
            self.task_manager.add_task(w)
        else:
            # if there is no func, we are in a decorator
            def _run_async(func):
                self.run_async(func, *args, **kwargs)
                return func
            return _run_async

    def run_forever(self, func=None, interval_ms=1000, *args, **kwargs):
        """Runs a function every interval_ms milliseconds"""
        if func is not None:
            if interval_ms < 0:
                print("Invalid interval! Defaulting to 1000ms")
                interval_ms = 1000
            t = PersistantWorker(func, float(interval_ms) / 1000, *args, **kwargs)
            self.task_manager.add_task(t)
        else:
            # if there is no func, we are in a decorator
            def _run_forever(func):
                self.run_forever(func, interval_ms, *args, **kwargs)
                return func
            return _run_forever

    def start_tasks(self):
        """Begins running event loop"""
        print("Starting arena-py client...")
        self.task_manager.run()

    async def sleep(self, interval_ms):
        """Public function for sleeping in aysnc functions"""
        await self.task_manager.sleep(float(interval_ms) / 1000)

    def disconnect(self):
        """Disconnects Paho MQTT client"""
        self.client.disconnect()
        print("Disconnected!")

    def on_connect(self, client, userdata, flags, rc):
        """Paho MQTT client on_connect callback"""
        if rc == 0:
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
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)

        # update object attributes, if possible
        if "object_id" in payload:
            # check for events/object updates
            event = None
            if "action" in payload and payload["action"] == "clientEvent":
                event = Event(**payload)
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

    def generate_event(self, obj, type):
        evt = Event(object_id=obj.object_id, type=type,
                    position=obj.data.position,
                    source="arena_lib_"+self.client_id)
        res = self._publish(evt, "clientEvent")
        if self.debug: print(res)
        return res

    @property
    def all_objects(self):
        """Returns all objects created by the user"""
        return Object.all_objects

    def add_object(self, obj):
        """Public function to create an object"""
        res = self._publish(obj, "create")
        if self.debug: print(res)
        return res

    def update_object(self, obj, **kwargs):
        """Public function to update an object"""
        obj.update_attributes(**kwargs)
        res = self._publish(obj, "update")
        if self.debug: print(res)
        return res

    def delete_object(self, obj):
        """Public function to delete an object"""
        payload = {
            "object_id": obj.object_id
        }
        res = self._publish(payload, "delete")
        Object.remove(obj)
        if self.debug: print(res)
        return res

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
        self.client.publish(topic, payload, qos=0)
        return payload

    def get_persisted_obj(self, object_id, broker, scene):
        """Returns a dictionary for a persisted object. [TODO] wrap the output as an Object"""
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}/{object_id}', creds=True)
        output = json.loads(data)
        return output

    def get_persisted_scene_option(self, broker, scene):
        """Returns a dictionary for scene-options. [TODO] wrap the output as a BaseObject"""
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}', creds=True)
        output = json.loads(data)
        return output

    def add_topic(sub, callback):
        """Subscribes to new topic and adds filter for callback to on_message()"""
        self.secondary_callbacks[sub] = callback
        self.client.subscribe(sub)


    def remove_topic(sub):
        """Unsubscribes to topic and removes filter for callback"""
        self.client.unsubscribe(sub)
