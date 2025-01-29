import uuid

from ..attributes import DataEvent
from ..base_object import *


class Event(BaseObject):
    """
    Event class. Wrapper around JSON for events.
    """
    def __init__(self, **kwargs):
        # "object_id" is required in kwargs, defaulted to random uuid4
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]

        # make "action" "clientEvent" by default and remove "action" from kwargs
        action = kwargs.get("action", "clientEvent")
        if "action" in kwargs: del kwargs["action"]

        # make "type" "mousedown" by default and remove "type" from kwargs
        _type = kwargs.get("type", "mousedown")
        if "type" in kwargs: del kwargs["type"]

        kwargs = kwargs.get("data", kwargs)
        data = DataEvent(**kwargs)
        super().__init__(
                object_id=object_id,
                action=action,
                type=_type,
                data=data
            )

    # TODO (mwfarb): We should standardize this json() transform into BaseObject from Object/Event/Program
    def json(self, **kwargs):
        json_payload = vars(self).copy()
        json_payload.update(kwargs)

        data = vars(json_payload["data"])
        json_data = {}
        for k, v in data.items():
            if v is None:
                json_data[k] = v

            # rotation should be in quaternions
            if "rotation" == k:
                rot = data["rotation"]
                # always publish quaternions on wire format to avoid persist euler->quat merges
                json_data["rotation"] = rot.quaternion

            else:
                json_data[k] = v

        json_payload["data"] = json_data

        return self.json_encode(json_payload)
