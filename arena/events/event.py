from ..base_object import *
from ..attributes import Data
import uuid


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
        data = Data(**kwargs)
        super().__init__(
                object_id=object_id,
                action=action,
                type=_type,
                data=data
            )
