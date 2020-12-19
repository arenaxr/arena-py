import uuid
import random
import sys, os
import time
import paho.mqtt.client as mqtt
from datetime import datetime

from attributes import *
from objects import *
from events import *
from utils import *
from event_loop import *

import auth

class Arena(object):
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
        self.debug = debug

        self.client = mqtt.Client(
            "pyClient-" + str(random.randrange(0, 1000000)), clean_session=True
        )

        data = auth.authenticate(REALM, SCENE, HOST, webhost=webhost,
                                                     debug=self.debug)
        if 'username' in data and 'token' in data:
            self.client.username_pw_set(username=data["username"], password=data["token"])
        print("=====")

        self.on_msg_callback = on_msg_callback
        self.new_obj_callback = new_obj_callback

        self.unspecified_objs_ids = set() # objects that exist in scene, but user does not have reference to
        self.task_manager = EventLoop(self.stop)

        # add mqtt client loop to list of tasks
        self.network_loop = Timer(self.run_network_loop, 0.01)
        self.task_manager.add_task(self.network_loop)

        if port is not None:
            self.client.connect(HOST, port)
        else:
            self.client.connect(HOST)

        self.client.subscribe(self.root_topic + "/#")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def run_network_loop(self):
        self.client.loop()

    def run_once(self, func, *args, **kwargs):
        w = Worker(func, *args, **kwargs)
        self.task_manager.add_task(w)

    def run_forever(self, func, interval_ms, **kwargs):
        if interval_ms < 0:
            print("Invalid interval! Defaulting to 1000ms")
            interval_ms = 1000
        t = Timer(func, float(interval_ms) / 1000, **kwargs)
        self.task_manager.add_task(t)

    def start_tasks(self):
        print("Starting arena-py client...")
        self.task_manager.run()

    def stop(self):
        self.client.disconnect()
        print("Disconnected!")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected!")
            print("=====")
        else:
            print("Connection error! Result code: " + rc)

    def on_message(self, client, userdata, msg):
        self.process_message(msg)

    def process_message(self, msg):
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)

        # update object attributes, if possible
        if "object_id" in payload:
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
            elif object_id not in self.unspecified_objs_ids and self.new_obj_callback:
                self.new_obj_callback(payload)
                self.unspecified_objs_ids.add(object_id)
            elif not event and self.on_msg_callback:
                self.on_msg_callback(payload)

    @property
    def all_objects(self):
        return Object.all_objects

    def add_object(self, obj):
        self.publish(obj, "create")

    def update_object(self, obj, **kwargs):
        obj.update_attributes(**kwargs)
        self.publish(obj, "update")

    def delete_object(self, obj):
        payload = {
            "object_id": obj.object_id,
            "action": "delete"
        }
        self.publish(payload, "delete")
        Object.remove(obj)

    def publish(self, obj, action):
        topic = self.root_topic + "/" + obj["object_id"]
        d = datetime.now().isoformat()[:-3]+"Z"
        if action != "delete":
            payload = obj.json(action=action, timestamp=d)
        else:
            payload = obj
            payload["timestamp"] = d
            payload = json.dumps(payload)
        self.client.publish(topic, payload, qos=0)

    def get_network_persisted_obj(self, object_id, broker, scene):
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}/{object_id}', creds=True)
        output = json.loads(data)
        return output

    def get_network_persisted_scene(self, broker, scene):
        # pass token to persist
        data = auth.urlopen(
            url=f'https://{broker}/persist/{scene}', creds=True)
        output = json.loads(data)
        return output
