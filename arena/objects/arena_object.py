import uuid

from ..base_object import *
from ..attributes import Animation, Data, Position, Rotation, Scale, ATTRIBUTE_KEYWORD_TRANSLATION
from ..utils import *


class Object(BaseObject):
    """
    Object class. Defines a generic object in the ARENA.
    """

    type = "object"
    object_type = "entity"
    all_objects = {} # dict of all objects created so far
    private_objects = {} # dict of all private objects created so far

    def __init__(self, evt_handler=None, update_handler=None, **kwargs):
        # "object_id" is required in kwargs, defaulted to random uuid4
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]

        # "persist" is required in kwargs, defaulted to false
        persist = kwargs.get("persist", False)
        if "persist" in kwargs: del kwargs["persist"]

        # special case for "parent" (can be an Object)
        if "parent" in kwargs and isinstance(kwargs["parent"], Object):
            kwargs["parent"] = kwargs["parent"].object_id

        # "ttl" is optional
        ttl = kwargs.get("ttl", None)
        if "ttl" in kwargs: del kwargs["ttl"]

        private = kwargs.get("private", False)
        if "private" in kwargs: del kwargs["private"]

        private_userid = kwargs.get("private_userid", None)
        if "private_userid" in kwargs: del kwargs["private_userid"]

        # remove timestamp, if exists
        if "timestamp" in kwargs: del kwargs["timestamp"]

        # remove "updatedAt", if exists
        if "updatedAt" in kwargs: del kwargs["updatedAt"]

        # remove "action", if exists
        if "action" in kwargs: del kwargs["action"]

        # default "object_type" to entity
        if "object_type" not in kwargs:
            kwargs["object_type"] = Object.object_type

        if "position" not in kwargs:
            kwargs["position"] = Position(0,0,0)

        if "rotation" not in kwargs:
            kwargs["rotation"] = Rotation(0,0,0)

        if "scale" not in kwargs:
            kwargs["scale"] = Scale(1,1,1)

        # print warning if object is being created with the same id as an existing object
        if Object.exists(object_id):
            if not Object.get(object_id).persist:
                print("[WARNING]", f"An object with object_id of {object_id} was already created. The previous object will be overwritten.")
            Object.remove(Object.get(object_id))

        # setup attributes in the "data" field
        data = kwargs.get("data", kwargs)
        data = Data(**data)
        super().__init__(
                object_id=object_id,
                type=Object.type,
                persist=persist,
                data=data
            )
        if ttl:
            self.ttl = ttl

        # This is with regard to its interaction
        if private:
            # Note: public objects *can* have private clicks, mouseover, etc.
            self.private = private

        if private_userid:
            self._private_userid = private_userid  # None is public
            self.private = True # private objects are always private interaction

        self.evt_handler = evt_handler
        self.update_handler = update_handler
        self.animations = []

        # add current object to all_objects dict
        Object.add(self)
        # If private, add to private_objects dict
        if private_userid:
            Object.add_private(self)

        self.delayed_prop_tasks = {}  # dict of delayed property tasks

    def update_attributes(self, evt_handler=None, update_handler=None, **kwargs):
        if evt_handler:
            self.evt_handler = evt_handler

        if update_handler:
            self.update_handler = update_handler

        if "data" not in self:
            return

        if "persist" in kwargs:
            del kwargs["persist"]
            self.persist = kwargs.get("private")

        if "ttl" in kwargs:
            del kwargs["ttl"]
            self.ttl = kwargs.get("ttl")

        if "private" in kwargs:
            del kwargs["private"]
            self.private = kwargs.get("private")

        if "private_userid" in kwargs:
            del kwargs["private_userid"]
            self._private_userid = kwargs.get("private_userid")
            self.private = True

        data = self.data
        Data.update_data(data, kwargs)

        if self.update_handler:
            self.update_handler(self)

    def dispatch_animation(self, animation):
        if isinstance(animation, (tuple, list)):
            self.animations += list(animation)
        elif isinstance(animation, Animation):
            self.animations += [animation]
        return self.animations

    def remove_animation_at_index(self, idx):
        if 0 <= idx < len(self.animations):
            return self.animations.pop(idx)
        return -1

    def clear_animations(self):
        self.animations = []

    @property
    def clickable(self):
        return "click_listener" in self.data or "clickable" in self.data

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        skipped_keys = ["evt_handler", "update_handler", "animations", "delayed_prop_tasks", "_private_userid"]
        json_payload = {k: v for k, v in vars(self).items() if k not in skipped_keys}
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data): # to be done by subclasses, if needed
        pass

    def json(self, **kwargs):
        json_data = {}
        json_payload = self.json_preprocess(**kwargs)
        data = vars(json_payload["data"])

        for k,v in data.items():
            if v is None:
                json_data[k] = v

            # color should be a hex string
            elif "color" == k:
                json_data["color"] = v.hex

            elif "material" == k:
                json_data["material"] = vars(v).copy()
                if "color" in v:
                    color = v["color"]
                    json_data["material"]["color"] = color.hex

            # rotation should be in quaternions
            elif "rotation" == k:
                rot = data["rotation"]
                # always publish quaternions on wire format to avoid persist euler->quat merges
                json_data["rotation"] = rot.quaternion

            elif "look_at" == k:
                if isinstance(v, str):
                    json_data["look-at"] = v
                elif isinstance(v, Object):
                    json_data["look-at"] = v.object_id

            # for animation, replace "start" and "end" with "from" and "to"
            elif isinstance(k, str) and "animation" == k[:len("animation")]:
                animation = vars(v).copy()
                Utils.dict_key_replace(animation, "start", "from")
                Utils.dict_key_replace(animation, "end", "to")
                json_data[k] = animation

            # Translate and remove underscores from any other keys.
            # Must be done last since ATTRIBUTE_KEYWORD_TRANSLATION contains all attributes,
            # which may interfere with special casing above from, say "rotation" for example.
            elif k in ATTRIBUTE_KEYWORD_TRANSLATION:
                json_data[ATTRIBUTE_KEYWORD_TRANSLATION[k]] = v

            # allow: likely unknown/misspelled attribute to this library version
            else:
                json_data[k] = v

        json_payload.pop("delayed_prop_tasks", None)

        json_payload["data"] = json_data
        self.json_postprocess(json_payload, json_data)
        return self.json_encode(json_payload)

    # methods for global objects dictionary
    @classmethod
    def get(cls, object_id):
        return Object.all_objects.get(object_id, None)

    @classmethod
    def add(cls, obj):
        object_id = obj.object_id
        Object.all_objects[object_id] = obj

    @classmethod
    def add_private(cls, obj):
        private_userid = getattr(obj, "_private_userid", None)
        if private_userid is None:
            raise ValueError("No private user id specified")
        if private_userid not in Object.private_objects:
            raise ValueError(f"User {private_userid} does not exist")
        Object.private_objects[private_userid][obj.object_id] = obj

    @classmethod
    def remove(cls, obj):
        object_id = obj.object_id
        del Object.all_objects[object_id]
        if (hasattr(obj, "delayed_prop_tasks")):
            for task in obj.delayed_prop_tasks.values():  # Cancel all pending tasks
                task.cancel()

    @classmethod
    def exists(cls, object_id):
        return object_id in Object.all_objects
