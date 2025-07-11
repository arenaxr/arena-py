import argparse
import asyncio
import json
import os
import re
import sys
import threading
import traceback
import uuid
from datetime import datetime
from inspect import signature
from pathlib import Path

import __main__ as main

from .arena_mqtt import ArenaMQTT
from .attributes import *
from .chat import *
from .env import PROGRAM_OBJECT_ID, SCENE, _get_env
from .events import *
from .objects import *
from .topics import PUBLISH_TOPICS, SCENE_MSGTYPES, TOPIC_TOKENS, TOPIC_TYPES
from .utils import (
    ArenaCmdInterpreter,
    ArenaTelemetry,
    ProgramRunInfo,
    QueueStats,
    Utils,
)


class Scene(ArenaMQTT):
    """
    Gives access to an ARENA scene.
    Can create and execute various user-defined functions/tasks.

    :param str host: Hostname of the ARENA webserver (required).
    :param str realm: Reserved topic fork for future use (optional).
    :param str namespace: Username of authenticated user or other namespace (automatic).
    :param str scene: The name of the scene, without namespace (required).
    :param int network_latency_interval: Interval (in ms) to run network graph latency update. Default value is 10000 (10 secs). Ignore this parameter (optional).
    :param func on_msg_callback: Called on all MQTT messages received (optional).
    :param func new_obj_callback: Called on object 'create' MQTT messages received (optional).
    :param func user_join_callback: Called on user id 'new' MQTT messages received (optional).
    :param func user_left_callback: Called on user id 'leave' MQTT messages received (optional).
    :param func delete_obj_callback: Called on object 'delete' MQTT messages received (optional).
    :param func end_program_callback: Called on MQTT disconnect (optional).
    :param func on_chat_callback: Called on chat messages received (optional).
    :param bool video: If true, request permissions for video conference (optional).
    :param bool debug: If true, print a log of all publish messages from this client (optional).
    :param bool cli_args: If true, require CLI standardized parameters (optional).
    :param bool headless: If true, force limited input device auth flow (optional).
    """

    def __init__(
        self,
        host="arenaxr.org",
        realm="realm",
        network_latency_interval=10000,  # run network latency update every 10s
        on_msg_callback=None,
        new_obj_callback=None,
        user_join_callback=None,
        user_left_callback=None,
        delete_obj_callback=None,
        end_program_callback=None,
        on_chat_callback=None,
        video=False,
        debug=False,
        cli_args=False,
        headless=False,
        **kwargs,
    ):

        # init telemetry
        self.telemetry = ArenaTelemetry()

        # setup event to let others wait on connection
        self.connected_evt = threading.Event()

        # start the command interpreter (if enabled by env variable)
        self.cmd_interpreter = ArenaCmdInterpreter(
            self,
            show_attrs=("config_data", "scene", "users", "all_objects", "run_info"),
            get_callables=("persisted_objs", "persisted_scene_option", "writable_scenes", "user_list"),
            start_cmd_event=self.connected_evt,
        )

        if cli_args:
            self.args = self.parse_cli(cli_args)
            if self.args["host"]:
                kwargs["host"] = self.args["host"]
            if self.args["namespace"]:
                kwargs["namespace"] = self.args["namespace"]
            if self.args["scene"]:
                kwargs["scene"] = self.args["scene"]
            if self.args["debug"]:
                debug = self.args["debug"]

        if os.environ.get(SCENE):
            self.scene = _get_env(SCENE)
            print(f"Using Scene from 'SCENE' env variable: {self.scene}")
        elif "scene" in kwargs and kwargs["scene"]:
            self.scene = kwargs["scene"]
            print(f"Using Scene from 'scene' input parameter: {self.scene}")
        else:
            self.exit("Scene argument (scene) is unspecified or None, aborting...")

        if re.search("/", self.scene):
            self.exit("Scene cannot include '/', aborting...")

        super().__init__(
            host,
            realm,
            network_latency_interval,
            on_msg_callback,
            end_program_callback,
            video,
            debug,
            headless,
            **kwargs,
        )

        with self.telemetry.start_span(f"init {self.namespace}/{self.scene}") as span:
            # 'init' span will track the remainder of the initialization

            # create a program object to describe this program
            # PROGRAM_OBJECT_ID allows to match the object id of persisted program object
            # when a program object with PROGRAM_OBJECT_ID is loaded from persist, it will replace this one
            self.program = Program(
                object_id=_get_env(PROGRAM_OBJECT_ID, super().client_id()),
                name=f"{self.namespace}/{self.scene}",
                filename=sys.argv[0],
                filetype="PY",
            )

            self.persist_host = self.config_data["ARENADefaults"]["persistHost"]
            self.persist_path = self.config_data["ARENADefaults"]["persistPath"]

            self.persist_url = f"https://{self.persist_host}{self.persist_path}{self.namespaced_target}"

            # set up callbacks
            self.new_obj_callback = new_obj_callback
            self.delete_obj_callback = delete_obj_callback
            self.user_join_callback = user_join_callback
            self.user_left_callback = user_left_callback
            self.on_chat_callback = on_chat_callback

            # objects that exist in the scene, but this scene instance does not have a reference to
            self.unspecified_object_ids = set()
            self.users = {}  # dict of all users

            # setup program run info to collect stats
            self.run_info = ProgramRunInfo(
                self.event_loop,
                queue_len_callable=lambda: self.get_rcv_pub_queue_len(),
                update_callback=self.run_info_update,
                web_host=self.web_host,
                namespace=self.namespace,
                scene=self.scene,
                realm=self.realm,
            )

            # Always use the the hostname specified by the user, or defaults.
            print(f"Loading: https://{self.web_host}/{self.namespace}/{self.scene}, realm={self.realm}")

            span.add_event(f"Loading: https://{self.web_host}/{self.namespace}/{self.scene}, realm={self.realm}")

    def parse_cli(self, cli_args=False):
        """
        Reusable command-line options to give apps flexible options to avoid hard-coding locations.
        """
        parser = argparse.ArgumentParser(
            description=(f"{Path(main.__file__).name} (arena-py) Application CLI"),
            epilog="Additional user-defined args are possible, see docs at https://docs.arenaxr.org/content/python/scenes for usage.",
        )
        parser.add_argument("-mh", "--host", type=str, help="ARENA webserver main host to connect to")
        parser.add_argument("-n", "--namespace", type=str, help="Namespace of scene")
        parser.add_argument("-s", "--scene", type=str, help="Scene to publish and listen to")
        parser.add_argument("-d", "--device", type=str, help="Device to publish and listen to")
        parser.add_argument("-p", "--position", nargs=3, type=float, default=(0, 0, 0), help="App position as 'x y z'")
        parser.add_argument("-r", "--rotation", nargs=3, type=float, default=(0, 0, 0), help="App rotation as 'x y z'")
        parser.add_argument("-c", "--scale", nargs=3, type=float, default=(0, 0, 0), help="App scale as 'x y z'")
        parser.add_argument("-D", "--debug", action="store_true", help="Debug mode.", default=False)

        # add known help descriptions
        if isinstance(cli_args, dict):
            for k in cli_args:
                parser.add_argument(f"-{k}", f"--{k}", help=cli_args[k], required=False)

        # add unknown arguments for users to pull as strings
        parsed, unknown = parser.parse_known_args()
        for arg in unknown:
            if arg.startswith(("-", "--")):
                parser.add_argument(arg.split("=")[0])

        args = parser.parse_args()
        argdict = vars(args)
        argdict["position"] = tuple(args.position)
        argdict["rotation"] = tuple(args.rotation)
        argdict["scale"] = tuple(args.scale)
        return argdict

    def exit(self, arg=None):
        """Custom exit to push errors to telemetry."""
        error_msg = None
        if arg != None and arg != 0:
            error_msg = f"Exiting with sys.exit('{arg}')"
        self.telemetry.exit(error_msg)
        os._exit(0 if error_msg == None else 1)

    def on_connect(self, client, userdata, flags, rc, properties):
        super().on_connect(client, userdata, flags, rc, properties)
        if rc == 0:
            # set event
            self.connected_evt.set()

            # create arena-py Objects from persist server
            # no need to return anything here
            self.get_persisted_objs()

    def on_message(self, client, userdata, msg):
        super().on_message(client, userdata, msg)
        self.run_info.msg_rcv()

    def on_message_private(self, client, userdata, msg):
        super().on_message_private(client, userdata, msg)
        self.run_info.msg_rcv()

    def on_publish(self, client, userdata, mid, rc, properties):
        self.run_info.msg_publish()

    async def process_message(self):
        while True:
            try:
                msg = await self.msg_queue.get()
            except RuntimeError as e:
                self.telemetry.add_event(f"Ignoring error: {e}")
                continue

            # extract payload
            try:
                payload_str = msg.payload.decode("utf-8", "ignore")
                payload = json.loads(payload_str)
            except Exception as e:
                self.telemetry.add_event(f"Malformed payload: {payload_str}. {e}.")
                continue

            if self.debug:
                # log messages received for debugging
                self.telemetry.add_event(f"[received] {msg.topic} {payload}")

            payload["topic"] = msg.topic  # add topic for downstream callbacks/handlers
            object_id = payload.get("object_id", None)
            action = payload.get("action", None)
            topic_split = msg.topic.split("/")

            # Validate scene messages object_id vs topic uuid token
            scene_msgtype = None
            if topic_split[TOPIC_TOKENS.TYPE] == TOPIC_TYPES.SCENE:
                topic_uuid = topic_split[TOPIC_TOKENS.UUID]
                if object_id != topic_uuid:
                    self.telemetry.set_error(f"Message object_id {object_id} does not match topic {topic_uuid}.")
                    continue
                scene_msgtype = topic_split[TOPIC_TOKENS.SCENE_MSGTYPE]
                # Handle chat messages without same payload expectations as other scene messages
                if self.on_chat_callback and scene_msgtype == SCENE_MSGTYPES.CHAT:
                    chatmsg = Chat(**payload)
                    self.callback_wrapper(self.on_chat_callback, chatmsg, msg)
                    continue
                # Object updates only in these scene msg types
                if scene_msgtype not in [SCENE_MSGTYPES.PRESENCE, SCENE_MSGTYPES.USER, SCENE_MSGTYPES.OBJECTS, SCENE_MSGTYPES.PROGRAM]:
                    continue

            with self.telemetry.start_process_msg_span(object_id, action) as span:
                try:
                    # update object attributes
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
                            # get object from target
                            if "target" in data and data["target"] in self.all_objects:
                                obj = self.all_objects[data["target"]]
                                if obj.evt_handler:
                                    self.callback_wrapper(obj.evt_handler, event, payload)
                                    continue
                            span.add_event("Client event: {event}")
                        elif action == "leave":
                            # special user presence message, new way to remove user
                            if object_id in self.users:
                                self.delete_user_objects(object_id)
                                if self.user_left_callback:
                                    self.callback_wrapper(self.user_left_callback, self.users[object_id], payload)
                                del self.users[object_id]
                            span.add_event("User left.")
                        elif action == "delete":
                            if Camera.object_type in object_id:  # object is a camera
                                # old way to remove user
                                if object_id in self.users:
                                    if self.user_left_callback:
                                        self.callback_wrapper(self.user_left_callback, self.users[object_id], payload)
                                    del self.users[object_id]
                            elif (
                                HandLeft.object_type in object_id or HandRight.object_type in object_id
                            ):  # object is a hand/controller
                                if "dep" in obj.data:
                                    user_id = obj.data.dep
                                    if user_id in self.users:
                                        user = self.users[user_id]
                                        if obj in user.hands.values():
                                            if user.hand_remove_callback:
                                                self.callback_wrapper(user.hand_remove_callback, obj, payload)
                                            hand_key = (
                                                HandLeft.object_type
                                                if HandLeft.object_type in object_id
                                                else HandRight.object_type
                                            )
                                            del user.hands[hand_key]
                            elif self.delete_obj_callback:
                                self.callback_wrapper(self.delete_obj_callback, obj, payload)
                            Object.remove(obj)
                            span.add_event("Object delete.")

                            continue

                        else:  # create/update
                            obj.update_attributes(**payload)
                            span.add_event("Object attributes update.")

                    else:
                        self.telemetry.set_error("No message action!", span)

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
                                self.reset_private_objects(object_id)

                                if self.user_join_callback:
                                    self.callback_wrapper(self.user_join_callback, self.users[object_id], payload)

                        elif object_type == HandLeft.object_type or object_type == HandRight.object_type:
                            if "dep" in obj.data:
                                user_id = obj.data.dep
                                if user_id in self.users:
                                    user = self.users[user_id]
                                    if obj not in user.hands.values():
                                        user.hands[object_type] = obj
                                        obj.camera = user

                                        if user.hand_found_callback:
                                            self.callback_wrapper(user.hand_found_callback, obj, payload)

                    # if its an object the library has not seen before, call new object callback
                    elif object_id not in self.unspecified_object_ids and self.new_obj_callback:
                        self.callback_wrapper(self.new_obj_callback, obj, payload)
                        self.unspecified_object_ids.add(object_id)
                        span.add_event("New Object.")

                    span.add_event("Handle Msg Done.")

                except Exception as e:
                    self.telemetry.set_error(
                        f"Something went wrong!\n"
                        f"-----------------------------\n"
                        f"Source:\n{traceback.format_exc()}\n\n"
                        f"Exception occured when processing payload: {payload}\n"
                        f"-----------------------------\n"
                    )

    def callback_wrapper(self, func, arg, msg):
        """Checks for number of arguments for callback."""
        if len(signature(func).parameters) != 3:
            print("[DEPRECATED]", "Callbacks and handlers now take 3 arguments: (scene, obj/evt, msg)!")
            func(arg)
        else:
            func(self, arg, msg)

    def generate_custom_event(self, evt, action="clientEvent"):
        """Publishes an custom event. Could be user or library defined."""
        return self._publish(evt, action)

    def generate_click_event(self, obj: Object, type="mousedown", **kwargs):
        """Publishes an click event."""
        _type = type
        evt = Event(
            object_id=self.mqttc_id, type=_type, targetPosition=obj.data.position, target=obj.object_id, **kwargs
        )
        return self.generate_custom_event(evt, action="clientEvent")

    def manipulate_camera(self, cam, **kwargs):
        """Publishes a camera manipulation event."""
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
        evt = Event(object_id=object_id, type="camera-override", object_type=Camera.object_type, **kwargs)
        return self.generate_custom_event(evt, action="update")

    def look_at(self, cam, target):
        """Publishes a camera manipulation event."""
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
        evt = Event(object_id=object_id, type="camera-override", object_type="look-at", target=target)
        return self.generate_custom_event(evt, action="update")

    def teleport_to_landmark(self, cam, target):
        """Publishes a camera manipulation event."""
        if isinstance(target, Object):
            target_id = target.object_id
        elif type(target) is str:
            target_id = target
        else:
            raise ValueError("target must be an ARENA object or string object_id")

        if isinstance(cam, Object):
            object_id = cam.object_id
        elif type(target) is str:
            object_id = cam
        else:
            raise ValueError("cam must be an ARENA object or string object_id")

        evt = Event(
            object_id=object_id, type="camera-override", object_type="teleport-to-landmark", landmarkObj=target_id
        )
        return self.generate_custom_event(evt, action="update")

    @property
    def all_objects(self):
        """Returns all the objects in a scene."""
        return Object.all_objects

    def get_private_objects(self, userid=None):
        """ Returns all private user objects."""
        if userid is not None:
            return Object.private_objects.get(userid, None)
        else:
            return Object.private_objects

    def reset_private_objects(self, userid):
        """Resets all private user objects."""
        Object.private_objects[userid] = {}

    def add_object(self, obj):
        """Public function to create an object."""
        if not isinstance(obj, Object):
            raise ValueError(f"Not a valid ARENA object to add to scene: {type(obj)}")
        # We have to set program_id here, as only scene has access to its userid
        if getattr(obj, "private", True):
            obj.program_id = self.userid
        res = self._publish(obj, "create")
        self.run_animations(obj)
        return res

    def add_objects(self, objs):
        """Public function to create multiple objects in a list."""
        for obj in objs:
            self.add_object(obj)
        return len(objs)

    def update_object(self, obj: Object, **kwargs):
        """Public function to update an object."""
        if kwargs:
            obj.update_attributes(**kwargs)

        # We have to update program_id here, as only scene has access to its userid
        if getattr(obj, "private", True):
            obj.program_id = self.userid

        # Check if any keys in delayed_prop_tasks are pending new animations
        # and cancel corresponding final update tasks or, if they are in
        # kwarg property updates, cancel the task as well as the animation
        if len(obj.delayed_prop_tasks) > 0:
            # If we have new animations that override a delayed task, cancel the task
            for anim in obj.animations:
                if anim.property in obj.delayed_prop_tasks:
                    task_to_cancel = obj.delayed_prop_tasks[anim.property]
                    task_to_cancel.cancel()
                    del task_to_cancel

            # If we have a property update that overrides a delayed task, cancel task
            # and cancel the animation
            for k in kwargs:
                if str(k) in obj.delayed_prop_tasks:
                    task_to_cancel = obj.delayed_prop_tasks[k]
                    task_to_cancel.cancel()
                    del task_to_cancel
                    obj.dispatch_animation(Animation(property=k, enabled=False, dur=0))

        res = self._publish(obj, "update")
        self.run_animations(obj)
        return res

    def update_objects(self, objs, **kwargs):
        """Public function to update multiple objects in a list."""
        for obj in objs:
            self.update_object(obj, **kwargs)
        return len(objs)

    def delete_object(self, obj):
        """Public function to delete an object."""
        payload = {"object_id": obj.object_id}
        Object.remove(obj)
        return self._publish(payload, "delete", custom_payload=True)

    def delete_user_objects(self, userid):
        """Deletes any private user objects."""
        if userid in Object.private_objects:
            for obj in Object.private_objects[userid].keys():
                Object.all_objects.pop(obj, None)
        del Object.private_objects[userid]

    def delete_program(self, obj):
        type=None
        try:
            type = obj.type
        except AttributeError:
            raise ValueError("obj must be of type Program!")
        if not type == Program.object_type: ValueError("obj must be of type Program!")

        # create runtime request (to delete program instance); TODO: Properly define a program instance/runtime request
        payload = {
            "object_id": str(uuid.uuid4()),
            "type": "req",
            "data": {
                "uuid": obj.object_id,
                "type": "module",
                "name": obj.data.name,
                "parent": obj.data.parent,
            },
        }
        Object.remove(obj)
        return self._publish(payload, "delete", custom_payload=True, publish_topic=PUBLISH_TOPICS.SCENE_PROGRAM)

    def delete_attributes(self, obj: Object, attributes=None):
        """Public function to delete a list of 'attributes' as a string[], updating each to null."""
        updated_data = {}
        for attr in attributes:
            obj.data[attr] = None  # remove from large internal storage
            updated_data[attr] = None  # remove from small external publish
        payload = {
            "object_id": obj.object_id,
            "type": obj.type,
            "persist": obj.persist,
            "data": updated_data,  # dashes handled from string array
        }
        return self._publish(payload, "update", custom_payload=True)

    def run_animations(self, obj: Object):
        """Runs all dispatched animations."""
        if isinstance(obj, Object):
            payload = {"object_id": obj.object_id, "type": obj.type, "data": {"object_type": obj.data.object_type}}
            if len(obj.animations) == 0:
                return
            for i, animation in enumerate(obj.animations):
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
        else:
            raise ValueError("obj must be of type Object!")

    def create_delayed_task(self, obj: Object, anim: Animation | AnimationMixer):
        """
        Creates a delayed task to push the end state of an animation after the expected
        duration. Uses async sleep to avoid blocking.
        :param obj: arena object to update.
        :param anim: Animation to run.
        :return: created async task.
        """

        async def _delayed_task():
            try:
                sleep_dur = (anim.get("dur", 0) + anim.get("delay", 0)) / 1000
                await asyncio.sleep(sleep_dur)  # this is in seconds
                final_state = anim["from"] if anim.get("dir", "normal") == "reverse" else anim["to"]
                obj.update_attributes(**{anim["property"]: final_state})
                self.update_object(obj)
                obj.delayed_prop_tasks.pop(anim["property"], None)
            except asyncio.CancelledError:
                self.telemetry.add_event(f"Animation end task cancelled for {obj.object_id}.{anim['property']}")

        if anim.get("loop", 0) or anim.get("enabled", True) is False:
            return None

        delayed_task = asyncio.create_task(_delayed_task())
        obj.delayed_prop_tasks[anim["property"]] = delayed_task
        delayed_task.object_id = obj.object_id
        return delayed_task

    def _publish(self, obj: Object, action, custom_payload=False, publish_topic=PUBLISH_TOPICS.SCENE_OBJECTS):
        """Publishes to mqtt broker with "action":action."""
        obj_type = None
        if "type" in obj:
            obj_type = obj["type"]

        with self.telemetry.start_publish_span(obj["object_id"], action, obj_type) as span:
            topic = publish_topic.substitute({**self.topicParams, **{"objectId": obj["object_id"]}})

            if publish_topic == PUBLISH_TOPICS.SCENE_OBJECTS:
                # self.can_publish_obj indicates if we can publish on the default publish_topic (PUBLISH_TOPICS.SCENE_OBJECTS)
                if not self.can_publish_obj:
                    self.telemetry.set_error(
                        f"ERROR: Publish failed! You do not have permission to publish to topic {topic} on {self.web_host}",
                        span,
                    )
                elif hasattr(obj, "_private_userid"):
                    topic = PUBLISH_TOPICS.SCENE_OBJECTS_PRIVATE.substitute(
                        {**self.topicParams, **{"objectId": obj['object_id'], "toUid": obj['_private_userid']}}
                    )

            d = datetime.utcnow().isoformat()[:-3] + "Z"

            if custom_payload:
                tmp_obj = obj
                tmp_obj["action"] = action
                tmp_obj["timestamp"] = d
                payload = json.dumps(tmp_obj)
            else:
                payload = obj.json(action=action, timestamp=d)

            # add warning to user that outgoing rotation is invalid if auto/manual units are incorrect
            if '"w": null' in payload:
                self.telemetry.set_error(
                    f"ERROR!! Publishing wire rotation data must be in Quaternion units, Euler conversion failed for payload: {payload}"
                )

            self.mqttc.publish(topic, payload, qos=0)
            if self.debug:
                self.telemetry.add_event(f"[publish] {topic} {payload}")
            return payload

    def get_persisted_obj(self, object_id):
        """Returns a dictionary for a persisted object.

        If object is known by arena-py, return local object, not persisted.
        """
        persist_obj = None
        if object_id in self.all_objects:
            persist_obj = self.all_objects[object_id]
            persist_obj.persist = True
        else:
            # pass token to persist
            data = self.auth.urlopen(url=f"{self.persist_url}/{object_id}", creds=True)
            persist_obj = json.loads(data)
            if len(persist_obj) > 0:
                persist_obj = persist_obj[0]

                obj_id = persist_obj.get("object_id", object_id)
                data = persist_obj.get("attributes", {})
                object_type = data.get("object_type")

                # special case for Program type
                if persist_obj.get("type") == Program.object_type:
                    object_type = Program.object_type

                if object_type != None:
                    obj_class = OBJECT_TYPE_MAP.get(object_type, Object)
                    persist_obj = obj_class(object_id=obj_id, data=data)
                    persist_obj.persist = True

        if not persist_obj:
            raise ValueError(f'object with object_id="{object_id}" not found in persist!')

        return persist_obj

    def get_persisted_objs(self):
        """Returns a dictionary of persisted objects.

        If object is known by arena-py, return our local object, not persisted.
        Silently fails/skip objects without object_id and object_type (except programs).
        Instantiates generic Object if object_type is given but unknown to arena-py.
        """
        objs = {}
        # pass token to persist
        data = self.auth.urlopen(url=self.persist_url, creds=True)
        output = json.loads(data)
        for obj in output:
            # note: no exception on missing fields
            object_id = obj.get("object_id")
            data = obj.get("attributes", {})
            object_type = data.get("object_type")

            # special case for Program type
            if obj.get("type") == Program.object_type:
                object_type = Program.object_type

            persisted_obj = None

            if object_id != None:
                if object_id in self.all_objects:
                    # note: object from our list (not from persist)
                    persisted_obj = self.all_objects[object_id]
                    persisted_obj.persist = True

                    # replace program object, if matches our program id
                    if object_type == Program.object_type:
                        if os.environ.get(PROGRAM_OBJECT_ID) == object_id:
                            print("PROGRAM_OBJECT_ID", object_id)
                            persisted_obj.persist = True
                            self.program = Program(object_id=object_id, **data)
                        else:
                            # dont persist program object if not ours
                            persisted_obj.persist = False

                elif object_type != None:
                    # note: instantiate even with empty attributes if object_type is unknown to arena-py
                    obj_class = OBJECT_TYPE_MAP.get(object_type, Object)
                    persisted_obj = obj_class(object_id=object_id, data=data)
                    persisted_obj.persist = True

                if persisted_obj is not None:
                    objs[object_id] = persisted_obj

        return objs

    def get_persisted_scene_option(self):
        """Returns a dictionary for scene-options."""
        # [TODO] wrap the output as a BaseObject
        scene_opts_url = f"{self.persist_url}?type=scene-options"
        # pass token to persist
        data = self.auth.urlopen(url=scene_opts_url, creds=True)
        output = json.loads(data)
        return output

    def get_writable_scenes(self):
        """Request list of scene names for logged in user account that user has publish permission for.

        :returns list: list of scenes.
        """
        return self.auth.get_writable_scenes(web_host=self.web_host)

    def get_user_list(self):
        """Returns a list of users."""
        return self.users.values()

    def get_rcv_pub_queue_len(self):
        """Return QueueStats object with receive and publish queue length."""
        return QueueStats(super().rcv_queue_len(), super().pub_queue_len())

    def run_info_update(self, run_info):
        """Callback when program stats are updated; publish program object update."""
        # Add run info to program data object and publish program object update
        run_info.add_program_info(self.program.data)
        self._publish(self.program, "update", publish_topic=PUBLISH_TOPICS.SCENE_PROGRAM)

    def upload_store_file(self, src_file_path, dest_file_path=None):
        """Upload a file to the filestore using the user's Google account.

        :param str src_file_path: Local path to the file to upload (required).
        :param str dest_file_path: Destination file path, can include dirs. Defaults to filename from src_file_path (optional).
        :return str: Url address of successful file upload location, or None if failed.
        """
        return self.auth.upload_store_file(
            web_host=self.web_host, scenename=self.scene, src_file_path=src_file_path, dest_file_path=dest_file_path
        )


class Arena(Scene):
    """
    Another name for Scene.
    """
