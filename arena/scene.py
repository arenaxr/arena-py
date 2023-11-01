import asyncio
import json
import os
import re
import sys
from datetime import datetime
from inspect import signature

from .arena_mqtt import ArenaMQTT
from .attributes import *
from .events import *
from .objects import *
from .utils import *

class Scene(ArenaMQTT):
    """
    Gives access to an ARENA scene.
    Can create and execute various user-defined functions/tasks.

    :param str host: Hostname of the ARENA webserver (required).
    :param str realm: Reserved topic fork for future use (optional).
    :param str namespace: Username of authenticated user or other namespace (automatic).
    :param str scene: The name of the scene, without namespace (required).
    """

    def __init__(
                self,
                host = "arenaxr.org",
                realm = "realm",
                network_latency_interval = 10000,  # run network latency update every 10s
                on_msg_callback = None,
                new_obj_callback = None,
                user_join_callback = None,
                user_left_callback = None,
                delete_obj_callback = None,
                end_program_callback = None,
                video = False,
                debug = False,
                cli_args = False,
                **kwargs
            ):
        if cli_args:
            self.args = self.parse_cli()
            if self.args["host"]:
                kwargs["host"] = self.args["host"]
            if self.args["namespace"]:
                kwargs["namespace"] = self.args["namespace"]
            if self.args["scene"]:
                kwargs["scene"] = self.args["scene"]
            if self.args["debug"]:
                debug = self.args["debug"]

        if os.environ.get("SCENE"):
            self.scene = os.environ["SCENE"]
            print(f"Using Scene from 'SCENE' env variable: {self.scene}")
        elif "scene" in kwargs and kwargs["scene"]:
            if re.search("/", kwargs["scene"]):
                sys.exit("Scene argument (scene) cannot include '/', aborting...")
            self.scene = kwargs["scene"]
            print(f"Using Scene from 'scene' input parameter: {self.scene}")
        else:
            sys.exit("Scene argument (scene) is unspecified or None, aborting...")

        super().__init__(
            host,
            realm,
            network_latency_interval,
            on_msg_callback,
            end_program_callback,
            video,
            debug,
            **kwargs
        )

        self.persist_host = self.config_data["ARENADefaults"]["persistHost"]
        self.persist_path = self.config_data["ARENADefaults"]["persistPath"]

        self.persist_url = f"https://{self.persist_host}{self.persist_path}{self.namespaced_target}"

        # set up callbacks
        self.new_obj_callback = new_obj_callback
        self.delete_obj_callback = delete_obj_callback
        self.user_join_callback = user_join_callback
        self.user_left_callback = user_left_callback

        self.unspecified_object_ids = set() # objects that exist in the scene,
                                            # but this scene instance does not
                                            # have a reference to
        self.users = {} # dict of all users

        # Always use the the hostname specified by the user, or defaults.
        print(f"Loading: https://{self.web_host}/{self.namespace}/{self.scene}, realm={self.realm}")

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            # create arena-py Objects from persist server
            # no need to return anything here
            self.get_persisted_objs()

    async def process_message(self):
        while True:
            try:
                msg = await self.msg_queue.get()
            except RuntimeError as e:
                print(f"Ignoring error: {e}")
                return

            # extract payload
            try:
                payload_str = msg.payload.decode("utf-8", "ignore")
                payload = json.loads(payload_str)
            except Exception as e:
                print("Malformed payload, ignoring:")
                print(e)
                return

            try:
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
                                if object_id in self.users:
                                    if self.user_left_callback:
                                        self.callback_wrapper(
                                                self.user_left_callback,
                                                self.users[object_id],
                                                payload
                                            )
                                    del self.users[object_id]
                            elif HandLeft.object_type in object_id or HandRight.object_type in object_id: # object is a hand/controller
                                if "dep" in obj.data:
                                    user_id = obj.data.dep
                                    if user_id in self.users:
                                        user = self.users[user_id]
                                        if obj in user.hands.values():
                                            if user.hand_remove_callback:
                                                self.callback_wrapper(
                                                        user.hand_remove_callback,
                                                        obj,
                                                        payload
                                                    )
                                            hand_key = HandLeft.object_type if HandLeft.object_type in object_id else HandRight.object_type
                                            del user.hands[hand_key]
                            elif self.delete_obj_callback:
                                self.callback_wrapper(self.delete_obj_callback, obj, payload)
                            Object.remove(obj)
                            continue

                        else: # create/update
                            obj.update_attributes(**payload)

                    # call new message callback for all messages
                    if self.on_msg_callback:
                        if not event:
                            self.callback_wrapper(self.on_msg_callback, obj, payload)
                        else:
                            self.callback_wrapper(self.on_msg_callback, event, payload)

                    if object_type:
                        # run user_join_callback when user is found
                        if object_type == Camera.object_type:
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

                        elif object_type == HandLeft.object_type or object_type == HandRight.object_type:
                            if "dep" in obj.data:
                                user_id = obj.data.dep
                                if user_id in self.users:
                                    user = self.users[user_id]
                                    if obj not in user.hands.values():
                                        user.hands[object_type] = obj
                                        obj.camera = user

                                        if user.hand_found_callback:
                                            self.callback_wrapper(
                                                user.hand_found_callback,
                                                obj,
                                                payload
                                            )

                    # if its an object the library has not seen before, call new object callback
                    elif object_id not in self.unspecified_object_ids and self.new_obj_callback:
                        self.callback_wrapper(self.new_obj_callback, obj, payload)
                        self.unspecified_object_ids.add(object_id)

            except Exception as e:
                print("Something went wrong, ignoring:")
                print(e)
                print(payload)

    def callback_wrapper(self, func, arg, msg):
        """Checks for number of arguments for callback"""
        if len(signature(func).parameters) != 3:
            print("[DEPRECATED]", "Callbacks and handlers now take 3 arguments: (scene, obj/evt, msg)!")
            func(arg)
        else:
            func(self, arg, msg)

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
            self.add_object(obj)
        return len(objs)

    def update_object(self, obj, **kwargs):
        """Public function to update an object"""
        if kwargs:
            obj.update_attributes(**kwargs)

        # Check if any keys in delayed_prop_tasks are pending new animations
        # and cancel corresponding final update tasks or, if they are in
        # kwarg property updates, cancel the task as well as the animation
        need_to_run_animations = False
        if len(obj.delayed_prop_tasks) > 0:
            for anim in obj.animations:
                if anim.property in obj.delayed_prop_tasks:
                    task_to_cancel = obj.delayed_prop_tasks[anim.property]
                    task_to_cancel.cancel()
                    del task_to_cancel

            for k in kwargs:
                if str(k) in obj.delayed_prop_tasks:
                    need_to_run_animations = True
                    task_to_cancel = obj.delayed_prop_tasks[k]
                    task_to_cancel.cancel()
                    del task_to_cancel
                    obj.dispatch_animation(
                        Animation(property=k, enabled=False, dur=0)
                    )
            if need_to_run_animations:
                self.run_animations(obj)

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
        return self._publish(payload, "delete", custom_payload=True)

    def delete_attributes(self, obj, attributes=None):
        """Public function to delete a list of 'attributes' as a string[], updating each to null"""
        updated_data = {}
        for attr in attributes:
            obj.data[attr] = None  # remove from large internal storage
            updated_data[attr] = None # remove from small external publish
        payload = {
            "object_id": obj.object_id,
            "type": obj.type,
            "persist": obj.persist,
            "data": updated_data  # dashes handled from string array
        }
        return self._publish(payload, "update", custom_payload=True)

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
                    payload["data"][f"animation__{anim['property']}"] = anim
                    Utils.dict_key_replace(anim, "start", "from")
                    Utils.dict_key_replace(anim, "end", "to")
                    self.create_delayed_task(obj, anim)
            obj.clear_animations()
            return self._publish(payload, "update", custom_payload=True)

    def create_delayed_task(self, obj, anim):
        """
        Creates a delayed task to push the end state of an animation after the expected
        duration. Uses async sleep to avoid blocking.
        :param obj: arena object to update
        :param anim: Animation to run
        :return: created async task
        """

        async def _delayed_task():
            try:
                sleep_dur = (anim.get('dur', 0) + anim.get('delay', 0)) / 1000
                await asyncio.sleep(sleep_dur)  # this is in seconds
                final_state = anim["from"] if anim.get("dir", "normal") == "reverse"\
                    else anim["to"]
                obj.update_attributes(**{anim["property"]: final_state})
                self.update_object(obj)
                obj.delayed_prop_tasks.pop(anim["property"], None)
            except asyncio.CancelledError:
                print("Animation end task cancelled for",
                      obj.object_id + "." + anim["property"])

        if anim.get("loop", 0) or anim.get("enabled", True) is False:
            return None

        delayed_task = asyncio.create_task(_delayed_task())
        obj.delayed_prop_tasks[anim["property"]] = delayed_task
        delayed_task.object_id = obj.object_id
        return delayed_task

    def _publish(self, obj, action, custom_payload=False):
        """Publishes to mqtt broker with "action":action"""
        if not self.can_publish:
            print(f"ERROR: Publish failed! You do not have permission to publish to topic {self.root_topic} on {self.web_host}")

        topic = f"{self.root_topic}/{self.mqttc_id}/{obj['object_id']}"
        d = datetime.utcnow().isoformat()[:-3]+"Z"

        if custom_payload:
            payload = obj
            payload["action"] = action
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
            data = self.auth.urlopen(url=f"{self.persist_url}/{object_id}", creds=True)
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
        data = self.auth.urlopen(url=self.persist_url, creds=True)
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
        data = self.auth.urlopen(url=scene_opts_url, creds=True )
        output = json.loads(data)
        return output

    def get_writable_scenes(self):
        """ Request list of scene names for logged in user account that user has publish permission for.
        Returns: list of scenes.
        """
        return self.auth.get_writable_scenes(web_host=self.web_host)

    def get_user_list(self):
        """Returns a list of users"""
        return self.users.values()

class Arena(Scene):
    """
    Another name for Scene.
    """
