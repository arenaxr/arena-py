import uuid
import signal
import random
import sys, os
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime

from attributes import *
from objects import *
from utils import *

import auth

class Arena(object):
    def __init__(self, host=None, scene=None, realm=None, port=None, callback=None, debug=False, webhost='xr.andrew.cmu.edu'):
        if os.environ.get('MQTTH') and os.environ.get('SCENE') and os.environ.get('REALM'):
            HOST  = os.environ["MQTTH"]
            SCENE = os.environ["SCENE"]
            REALM = os.environ["REALM"]
        else:
            print("Cannot find SCENE, MQTTH, and REALM environment variables, using input parameters instead.")
            if host and scene and realm:
                HOST  = host
                SCENE = scene
                REALM = realm
            else:
                sys.exit("scene, host, and realm are unspecified, aborting...")

        print(f"Loading: {HOST}/{SCENE}, realm={REALM}")
        print("=====")

        self.root_topic = f"{REALM}/s/{SCENE}"

        self.client = mqtt.Client(
            "pyClient-" + str(random.randrange(0, 1000000)), clean_session=True
        )

        data = auth.authenticate(REALM, SCENE, HOST, webhost=webhost,
                                                     debug=debug)
        if 'username' in data and 'token' in data:
            self.client.username_pw_set(username=data["username"], password=data["token"])
        print("=====")

        self.msg_queue = []
        self.msg_ready = threading.Event()
        self.running = False
        self.callback = callback
        self.debug = debug

        if port is not None:
            self.client.connect(HOST, port)
        else:
            self.client.connect(HOST)

        self.client.subscribe(self.root_topic + "/#")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        signal.signal(signal.SIGINT, self.signal_handler)

        self.client.loop_start()

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        print("Started network loop!")
        self.running = True
        while self.running:
            if len(self.msg_queue) > 0:
                self.process_message(self.msg_queue.pop(0))
            else:
                self.msg_ready.clear()
                self.msg_ready.wait()

    def signal_handler(self, sig, frame):
        self.running = False
        self.client.loop_stop()  # stop loop
        print("Disconnecting...")
        self.client.disconnect()
        sys.exit("Disconnected!")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected!")
        else:
            print("Connection error! Result code: " + rc)

    def on_message(self, client, userdata, msg):
        self.msg_queue.append(msg)
        self.msg_ready.set()

    def process_message(self, msg):
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)

        # update object attributes, if possible
        if "object_id" in payload:
            object_id = payload["object_id"]
            if object_id in Object.all_objects:
                obj = Object.all_objects[object_id]
                obj.update_attributes(data=payload["data"])
                if obj.callback:
                    obj.callback(payload_str)

        if self.callback:
            self.callback(payload)

    @property
    def all_objects(self):
        return Object.all_objects

    def add_object(self, obj):
        self.publish(obj, "create")

    def update_object(self, obj):
        self.publish(obj, "update")

    def delete_object(self, obj):
        payload = {
            "object_id": obj.object_id,
            "action": "delete"
        }
        self.publish(payload, "delete")
        Object.remove(obj)

    def publish(self, obj, action):
        topic = self.root_topic
        d = datetime.now().isoformat()[:-3]+"Z"
        if action != "delete":
            payload = obj.json(action=action, timestamp=d)
        else:
            payload = obj
            payload["timestamp"] = d
            payload = json.dumps(payload)
        self.client.publish(topic, payload, qos=0)
