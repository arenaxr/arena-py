from ..base_object import *
from ..attributes import Data
from ..utils import *
import uuid


class Object(BaseObject):
    """
    Object class. Defines a generic object in the ARENA.
    """

    all_objects = {} # dict of all objects created so far

    def __init__(self, evt_handler=None, **kwargs):
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

        # remove timestamp, if exists
        if "timestamp" in kwargs: del kwargs["timestamp"]

        # remove "action", if exists
        if "action" in kwargs: del kwargs["action"]

        # print warning if object is being created with the same id as an existing object
        if Object.exists(object_id):
            print("[WARNING]", f"An object with object_id of {object_id} was already created. The previous object will be overwritten.")
            Object.remove(Object.get(object_id))

        # setup attributes in the "data" field
        data = kwargs.get("data", kwargs)
        data = Data(**data)
        if ttl:
            super().__init__(
                    object_id=object_id,
                    type="object",
                    persist=persist,
                    ttl=ttl,
                    data=data
                )
        else:
            super().__init__(
                    object_id=object_id,
                    type="object",
                    persist=persist,
                    data=data
                )

        self.evt_handler = evt_handler

        # add current object to all_objects dict
        Object.add(self)

    def update_attributes(self, evt_handler=None, **kwargs):
        if evt_handler:
            self.evt_handler = evt_handler

        if "data" not in self:
            return

        # update "persist", and "ttl"
        self.persist = kwargs.get("persist", self.persist)
        if "ttl" in self:
            self.ttl = kwargs.get("ttl", self.ttl)

        data = self.data
        Data.update_data(data, kwargs)

    def json(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        res = { k:v for k,v in vars(self).items() if k != "evt_handler" }
        res.update(kwargs)

        data = res["data"].__dict__.copy()

        # color should be a hex string
        if "color" in data:
            data["color"] = data["color"].hex

        # rotation should be in quaternions
        if "rotation" in data:
            data["rotation"] = data["rotation"].quaternion

        # handle special case where "physics" should be "dynamic-body"
        if "physics" in data:
            ref = data["physics"]
            del data["physics"]
            data["dynamic-body"] = ref

        # handle special case where "clickable" should be "click-listener"
        if "clickable" in data:
            ref = data["clickable"]
            del data["clickable"]
            data["click-listener"] = ref

        # remove underscores from specific keys
        if "goto_url" in data:
            ref = data["goto_url"]
            del data["goto_url"]
            data["goto-url"] = ref

        if "click_listener" in data:
            ref = data["click_listener"]
            del data["click_listener"]
            data["click-listener"] = ref

        if "dynamic_body" in data:
            ref = data["dynamic_body"]
            del data["dynamic_body"]
            data["dynamic-body"] = ref

        # for animation, replace "start" and "end" with "from" and "to"
        if "animation" in data:
            animation = data["animation"].__dict__.copy()
            if "start" in animation:
                animation["from"] = animation["start"]
                del animation["start"]
            if "end" in animation:
                animation["to"] = animation["end"]
                del animation["end"]
            data["animation"] = animation

        res["data"] = data
        return self.json_encode(res)

    # methods for global object dictionary
    @classmethod
    def get(cls, object_id):
        return Object.all_objects.get(object_id, None)

    @classmethod
    def add(cls, obj):
        object_id = obj.object_id
        Object.all_objects[object_id] = obj

    @classmethod
    def remove(cls, obj):
        object_id = obj.object_id
        del Object.all_objects[object_id]

    @classmethod
    def exists(cls, object_id):
        return object_id in Object.all_objects
