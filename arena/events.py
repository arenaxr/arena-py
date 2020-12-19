from .base_object import *
from .attributes import Data
import uuid

class Event(BaseObject):
    """
    Event class. Wrapper around JSON for events.
    """
    def __init__(self, **kwargs):
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]
        action = kwargs.get("action", False)
        if "action" in kwargs: del kwargs["action"]
        type = kwargs.get("type", False)
        if "type" in kwargs: del kwargs["type"]

        kwargs = kwargs.get("data", kwargs)
        data = Data(**kwargs)
        super().__init__(
                object_id=object_id,
                action=action,
                type=type,
                data=data
            )
