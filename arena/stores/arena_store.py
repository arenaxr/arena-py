from arena.stores import json_store
from ..base_object import *
from ..attributes import Data
from ..utils import *
import uuid

class Store(BaseObject):
    """
    Store class. Defines a generic store in the ARENA.
    """

    type = "store"
    object_type = "entity"
    all_stores = {} # dict of all stores created so far

    def __init__(self, evt_handler=None, update_handler=None, **kwargs):
        # "object_id" is required in kwargs, defaulted to random uuid4
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]

        # "persist" is required in kwargs, defaulted to false
        persist = kwargs.get("persist", False)
        if "persist" in kwargs: del kwargs["persist"]

        # "ttl" is optional
        ttl = kwargs.get("ttl", None)
        if "ttl" in kwargs: del kwargs["ttl"]

        # remove timestamp, if exists
        if "timestamp" in kwargs: del kwargs["timestamp"]

        # remove "updatedAt", if exists
        if "updatedAt" in kwargs: del kwargs["updatedAt"]

        # remove "action", if exists
        if "action" in kwargs: del kwargs["action"]

        # default "object_type" to entity
        if "object_type" not in kwargs:
            kwargs["object_type"] = Store.object_type

        # print warning if object is being created with the same id as an existing object
        if Store.exists(object_id):
            if not Store.get(object_id).persist:
                print("[WARNING]", f"A store with object_id of {object_id} was already created. The previous object will be overwritten.")
            Store.remove(Store.get(object_id))

        # # setup attributes in the "data" field
        data = kwargs.get("data", kwargs)
        data = Data(**data)
        super().__init__(
                object_id=object_id,
                type=Store.type,
                persist=persist,
                data=data
            )
        if ttl:
            self.ttl = ttl

        self.evt_handler = evt_handler
        self.update_handler = update_handler
        self.animations = []

        # add current object to all_stores dict
        Store.add(self)

    def update_attributes(self, evt_handler=None, update_handler=None, **kwargs):
        if evt_handler:
            self.evt_handler = evt_handler

        if update_handler:
            self.update_handler = update_handler

        if "data" not in self:
            return

        # update "persist", and "ttl"
        self.persist = kwargs.get("persist", self.persist)
        if "ttl" in self:
            self.ttl = kwargs.get("ttl", self.ttl)

        if self.update_handler:
            self.update_handler(self)

    def update_store(self, **kwargs):
        if "data" not in self:
            return

        # Base store type does not hold any data or attributes
        # So nothing to do

        if self.update_handler:
            self.update_handler(self)

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        json_payload = { k:v for k,v in vars(self).items() if k != "evt_handler" and \
                                            k != "update_handler" and k != "animations" }
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data): # to be done by subclasses, if needed
        pass

    def json(self, data=None, **kwargs):
        json_data = {}
        json_payload = self.json_preprocess(**kwargs)
        if data is None:
            data = vars(json_payload["data"])
        else:
            data["object_type"] = self.object_type

        for k,v in data.items():
            json_data[k] = v

        json_payload["data"] = json_data
        self.json_postprocess(json_payload, json_data)
        return self.json_encode(json_payload)

    # methods for global objects dictionary
    @classmethod
    def get(cls, object_id):
        return Store.all_stores.get(object_id, None)

    @classmethod
    def add(cls, obj):
        object_id = obj.object_id
        Store.all_stores[object_id] = obj

    @classmethod
    def remove(cls, obj):
        object_id = obj.object_id
        del Store.all_stores[object_id]

    @classmethod
    def exists(cls, object_id):
        return object_id in Store.all_stores
