import os
import sys
import json
import random
import socket
import asyncio

import paho.mqtt.client as mqtt
from datetime import datetime
from inspect import signature

from .attributes import *
from .objects import *
from .events import *
from .utils import *
from .event_loop import *

from . import auth

class Scene(object):
    """
    Gives access to an ARENA scene.
    Wrapper around Paho MQTT client and EventLoop.
    Can create and execute various user-defined functions/tasks.
    """
    def __init__(
                self,
                network_latency_interval = 10000,  # run network latency update every 10s
                on_msg_callback = None,
                new_obj_callback = None,
                user_join_callback = None,
                user_left_callback = None,
                delete_obj_callback = None,
                end_program_callback = None,
                debug = False,
                **kwargs
            ):
        if os.environ.get("MQTTH"):
            self.host  = os.environ["MQTTH"]
        elif "host" in kwargs:
            self.host = kwargs["host"]
            print("Cannot find MQTTH environmental variable, using input parameter instead.")
        else:
            sys.exit("mqtt host argument (host) is unspecified, aborting...")

        if os.environ.get("REALM"):
            self.realm  = os.environ["REALM"]
        elif "realm" in kwargs:
            self.realm = kwargs["realm"]
            print("Cannot find REALM environmental variable, using input parameter instead.")
        else:
            sys.exit("realm argument (realm) is unspecified, aborting...")

        if os.environ.get("SCENE"):
            self.scene  = os.environ["SCENE"]
        elif "scene" in kwargs:
            self.scene = kwargs["scene"]
            print("Cannot find SCENE environmental variable, using input parameter instead.")
        else:
            sys.exit("scene argument (scene) is unspecified, aborting...")

        self.debug = debug

        print("=====")
        # do user auth
        username = None
        password = None
        if os.environ.get("ARENA_USERNAME") and os.environ.get("ARENA_PASSWORD"):
            username = os.environ["ARENA_USERNAME"]
            password = os.environ["ARENA_PASSWORD"]
        else:
            username = auth.authenticate_user(self.host, debug=self.debug)

        if os.environ.get("NAMESPACE"):
            self.namespace = os.environ["NAMESPACE"]
        elif "namespace" not in kwargs:
            self.namespace = username
        else:
            self.namespace = kwargs["namespace"]

        self.mqttc_id = "pyClient-" + self.generate_client_id()

        # set up scene variables
        self.namespaced_scene =  f"{self.namespace}/{self.scene}"

        self.root_topic = f"{self.realm}/s/{self.namespaced_scene}"
        self.scene_topic = f"{self.root_topic}/#"   # main topic for entire scene
        self.persist_url = f"https://{self.host}/persist/{self.namespaced_scene}"

        self.latency_topic = "$NETWORK/latency"     # network graph latency update
        self.ignore_topic = f"{self.root_topic}/{self.mqttc_id}/#" # ignore own messages

        self.mqttc = mqtt.Client(
            self.mqttc_id, clean_session=True
        )

        # do scene auth
        if username is None or password is None:
            data = auth.authenticate_scene(
                            self.host, self.realm,
                            self.namespaced_scene, username,
                            self.debug
                        )
            if 'username' in data and 'token' in data:
                username = data["username"]
                password = data["token"]
        self.mqttc.username_pw_set(username=username, password=password)
        print("=====")

        # set up callbacks
        self.on_msg_callback = on_msg_callback
        self.new_obj_callback = new_obj_callback
        self.delete_obj_callback = delete_obj_callback
        self.user_join_callback = user_join_callback
        self.user_left_callback = user_left_callback
        self.end_program_callback = end_program_callback

        self.unspecified_object_ids = set() # objects that exist in the scene,
                                          # but this scene instance does not
                                          # have a reference to
        self.users = {} # dict of all users
        self.landmarks = Landmarks() # scene landmarks

        self.task_manager = EventLoop(self.disconnect)

        aioh = AsyncioMQTTHelper(self.task_manager, self.mqttc)

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
            self.mqttc.connect(self.host, kwargs["port"])
        else:
            self.mqttc.connect(self.host)
        self.mqttc.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        print(f"Loading: https://{self.host}/{self.namespace}/{self.scene}, realm={self.realm}")

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
            t = PersistentWorker(func, self.mqtt_connect_evt, interval_ms, **kwargs)
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

    def stop_tasks(self):
        """Stop event loop"""
        self.task_manager.stop()

    async def sleep(self, interval_ms):
        """Public function for sleeping in async functions"""
        await asyncio.sleep(interval_ms / 1000)

    def on_connect(self, client, userdata, flags, rc):
        """Paho MQTT client on_connect callback"""
        if rc == 0:
            self.mqtt_connect_evt.set()

            # listen to all messages in scene
            client.subscribe(self.scene_topic)
            client.message_callback_add(self.scene_topic, self.on_message)

            # create ARENA-py Objects from persist server
            # no need to return anything here
            self.get_persisted_objs()

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
        """Main message processing function"""
        while True:
            msg = await self.msg_queue.get()

            # extract payload
            try:
                payload_str = msg.payload.decode("utf-8", "ignore")
                payload = json.loads(payload_str)
            except:
                return

            # update object attributes, if possible
            if "object_id" in payload:
                # parese payload
                object_id = payload.get("object_id", None)
                action = payload.get("action", None)

                data = payload.get("data", {})
                object_type = data.get("object_type", None)

                event = None

                # create/get object from object_id
                if object_id in self.all_objects:
                    obj = self.all_objects[object_id]
                else:
                    ObjClass = OBJECT_TYPE_MAP.get(object_type, Object)
                    obj = ObjClass(**payload)

                # react to action accordingly
                if action:
                    if action == "clientEvent":
                        event = Event(**payload)
                        if obj.evt_handler:
                            self.callback_wrapper(obj.evt_handler, event, payload)
                            continue

                    elif action == "delete":
                        if Camera.object_type in object_id: # object is a camera
                            if object_id in self.users and self.user_left_callback:
                                self.callback_wrapper(
                                        self.user_left_callback,
                                        self.users[object_id],
                                        payload
                                    )
                        elif self.delete_obj_callback:
                            self.callback_wrapper(self.delete_obj_callback, obj, payload)
                        continue

                    else: # create/update
                        obj.update_attributes(**payload)

                # call new message callback for all messages
                if self.on_msg_callback:
                    if not event:
                        self.callback_wrapper(self.on_msg_callback, obj, payload)
                    else:
                        self.callback_wrapper(self.on_msg_callback, event, payload)

                # run user_join_callback when user is found
                if object_type and object_type == Camera.object_type:
                    if object_id not in self.users:
                        if object_id in self.all_objects:
                            self.users[object_id] = obj
                        else:
                            self.users[object_id] = Camera(**payload)

                        if self.user_join_callback:
                            self.callback_wrapper(
                                    self.user_join_callback,
                                    self.users[object_id],
                                    payload
                                )

                # if its an object the library has not seen before, call new object callback
                elif object_id not in self.unspecified_object_ids and self.new_obj_callback:
                    self.callback_wrapper(self.new_obj_callback, obj, payload)
                    self.unspecified_object_ids.add(object_id)

    def callback_wrapper(self, func, arg, msg):
        """Checks for number of arguments for callback"""
        if len(signature(func).parameters) != 3:
            print("[DEPRECATED]", "Callbacks and handlers now take 3 arguments: (scene, obj/evt, msg)!")
            func(arg)
        else:
            func(self, arg, msg)

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
        if kwargs.get("position"):
            if isinstance(kwargs["position"], (list, tuple)):
                kwargs["position"] = Position(*kwargs["position"])
            elif isinstance(kwargs["position"], dict):
                kwargs["position"] = Position(**kwargs["position"])

        if kwargs.get("rotation"):
            if isinstance(kwargs["rotation"], (list, tuple)):
                kwargs["rotation"] = Rotation(*kwargs["rotation"])
            elif isinstance(kwargs["rotation"], dict):
                kwargs["rotation"] = Rotation(**kwargs["rotation"])

        if isinstance(cam, Object):
            object_id = cam.object_id
        else:
            object_id = cam
        evt = Event(object_id=object_id,
                    type="camera-override",
                    object_type=Camera.object_type,
                    **kwargs)
        return self.generate_custom_event(evt, action="update")

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
        return self.generate_custom_event(evt, action="update")

    def add_landmark(self, obj, label):
        """Adds a landmark to the scene"""
        if isinstance(obj, Object):
            landmark_id = obj.object_id
        else:
            landmark_id = Object
        # object must be persisted to make landmarks make sense
        obj.persist = True
        self.add_object(obj)
        self.landmarks.add(landmark_id, label)
        return self._publish(self.landmarks, "create")

    @property
    def all_objects(self):
        """Returns all the objects in a scene"""
        return Object.all_objects

    def add_object(self, obj):
        """Public function to create an object"""
        res = self._publish(obj, "create")
        self.run_animations(obj)
        return res

    def add_objects(self, objs):
        """Public function to create multiple objects in a list"""
        for obj in objs:
            self.add_objects(obj)
        return len(objs)

    def update_object(self, obj, **kwargs):
        """Public function to update an object"""
        if kwargs:
            obj.update_attributes(**kwargs)
        res = self._publish(obj, "update")
        self.run_animations(obj)
        return res

    def update_objects(self, objs, **kwargs):
        """Public function to update multiple objects in a list"""
        for obj in objs:
            self.update_object(obj, **kwargs)
        return len(objs)

    def delete_object(self, obj):
        """Public function to delete an object"""
        payload = {
            "object_id": obj.object_id
        }
        Object.remove(obj)
        return self._publish(payload, "delete")

    def run_animations(self, obj):
        """Runs all dispatched animations"""
        if obj.animations:
            payload = {
                "object_id": obj.object_id,
                "type": obj.type,
                "data": {"object_type": obj.data.object_type}
            }
            for i,animation in enumerate(obj.animations):
                if isinstance(animation, AnimationMixer):
                    payload["data"][f"animation-mixer"] = vars(animation)
                else:
                    anim = vars(animation).copy()
                    if i == 0:
                        payload["data"][f"animation"] = anim
                    else:
                        payload["data"][f"animation__{i}"] = anim
                    Utils.dict_key_replace(anim, "start", "from")
                    Utils.dict_key_replace(anim, "end", "to")
            obj.clear_animations()
            return self._publish(payload, "dispatch_animation")

    def _publish(self, obj, action):
        """Publishes to mqtt broker with "action":action"""
        topic = f"{self.root_topic}/{self.mqttc_id}/{obj['object_id']}"
        d = datetime.now().isoformat()[:-3]+"Z"

        if action == "delete":
            payload = obj
            payload["action"] = "delete"
            payload["timestamp"] = d
            payload = json.dumps(payload)
        elif action == "dispatch_animation":
            payload = obj
            payload["action"] = "update"
            payload["timestamp"] = d
            payload = json.dumps(payload)
        else:
            payload = obj.json(action=action, timestamp=d)

        self.mqttc.publish(topic, payload, qos=0)
        if self.debug: print("[publish]", topic, payload)
        return payload

    def get_persisted_obj(self, object_id):
        """Returns a dictionary for a persisted object."""
        obj = None
        if object_id in self.all_objects:
            obj = self.all_objects[object_id]
            obj.persist = True
        else:
            # pass token to persist
            data = auth.urlopen(url=f"{self.persist_url}/{object_id}", creds=True)
            output = json.loads(data)
            if len(output) > 0:
                output = output[0]

                object_id = output["object_id"]
                data = output["attributes"]
                object_type = data.get("object_type", None)

                ObjClass = OBJECT_TYPE_MAP.get(object_type, Object)
                obj = ObjClass(object_id=object_id, data=data)
                obj.persist = True

        return obj

    def get_persisted_objs(self):
        """Returns a dictionary of persisted objects. [TODO] check object_type"""
        objs = {}
        # pass token to persist
        data = auth.urlopen(url=self.persist_url, creds=True)
        output = json.loads(data)
        for obj in output:
            if obj["type"] == Object.object_type or obj["type"] == Object.type:
                object_id = obj["object_id"]
                data = obj["attributes"]

                if object_id in self.all_objects:
                    persisted_obj = self.all_objects[object_id]
                    persisted_obj.persist = True
                else:
                    object_type = data.get("object_type", None)
                    ObjClass = OBJECT_TYPE_MAP.get(object_type, Object)
                    persisted_obj = ObjClass(object_id=object_id, data=data)
                    persisted_obj.persist = True

                objs[object_id] = persisted_obj

        return objs

    def get_persisted_scene_option(self):
        """Returns a dictionary for scene-options. [TODO] wrap the output as a BaseObject"""
        scene_opts_url = f"{self.persist_url}?type=scene-options"
        # pass token to persist
        data = auth.urlopen(url=scene_opts_url, creds=True )
        output = json.loads(data)
        return output


    def get_writable_scenes(self):
        """ Request list of scene names for logged in user account that user has publish permission for.
        Returns: list of scenes.
        """
        return auth.get_writable_scenes(host=self.host, debug=self.debug)


    def message_callback_add(self, sub, callback):
        """Subscribes to new topic and adds callback"""
        self.mqttc.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        """Unsubscribes to topic and removes filter for callback"""
        self.mqttc.message_callback_remove(sub)

    def get_user_list(self):
        """Returns a list of users"""
        return self.users.values()

class Arena(Scene):
    """
    Another name for Scene.
    """
