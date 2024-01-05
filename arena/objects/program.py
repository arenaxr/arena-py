from ..base_object import *
from .arena_object import Object
from ..attributes import Data
import uuid
import os

from ..env_vars import (
    PROGRAM_OBJECT_ID,
)

class Program(BaseObject):
    """
    Program object in an ARENA Scene.

    :param str name: Name of the program 
    :param str affinity: Indicates the module affinity (client=client's runtime; none or empty=any suitable/available runtime)
    :param str instantiate: Single instance of the program (=single), or let every client create a program instance (=client). Per client instance will create new uuid for each program.
    :param str filename: Filename of the entry binary
    :param str filetype: Type of the program (WA=WASM or PY=Python)
    :param str parent: Request to deploy to this runtime (can be a runtime name or UUID); usually left blank.
    :param str[] args: Command-line arguments (passed in argv); e.g. [ "arg=value" ]. 
    :param str[] env: Environment variables; e.g. [ "SCENE=ascene" ].
    
    
    Uses env variable PROGRAM_OBJECT_ID to identify persist program object that represents the running program;
    """

    type = "program"
    object_type = "program"
    
    # save the program object the represents the running program instance
    running_instance = None
 
    def __init__(self, object_id=str(uuid.uuid4()), persist=False, **kwargs):

        if os.environ.get(PROGRAM_OBJECT_ID) == object_id:
            Program.running_instance = self
            
        # remove timestamp, if exists
        if "timestamp" in kwargs: del kwargs["timestamp"]

        # remove "updatedAt", if exists
        if "updatedAt" in kwargs: del kwargs["updatedAt"]

        # remove "action", if exists
        if "action" in kwargs: del kwargs["action"]

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
                type=Program.type,
                persist=persist,
                data=data
            )

        # add current object to all_objects dict
        Object.add(self)

    def update_attributes(self, evt_handler=None, update_handler=None, **kwargs):
        if "data" not in self:
            return

        # update "persist"
        self.persist = kwargs.get("persist", self.persist)

        data = self.data
        Data.update_data(data, kwargs)

    def json(self, **kwargs):
        json_data = {}
        json_payload = { k: v for k, v in vars(self).items() }
        json_payload.update(kwargs)
        data = vars(json_payload["data"])

        for k,v in data.items():
            if v is None:
                json_data[k] = v

        json_payload["data"] = data
        return self.json_encode(json_payload)

    @classmethod
    def running_instance_stats(cls, stats):
        if Program.running_instance:
            Program.running_instance.data['info'] = stats
            Program.running_instance.persist = True
            return Program.running_instance
        return None
    