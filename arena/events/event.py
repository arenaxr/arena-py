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

        # consume "object" so it lands on the Event itself. Left in kwargs it
        # would fall through into DataEvent (which has no Object-rejection
        # guard) and ride onto the wire nested under "data", or be dropped
        # outright when the caller also passed a "data" dict. Either way the
        # caller's object never reaches the attribute they asked for.
        _object = kwargs.get("object", None)
        if "object" in kwargs: del kwargs["object"]

        kwargs = kwargs.get("data", kwargs)
        data = DataEvent(**kwargs)
        super().__init__(
                object_id=object_id,
                action=action,
                type=_type,
                data=data,
                # the scene Object this event targets, when it is known locally.
                # Scene fills it in for inbound events whose target it can resolve;
                # events a program builds itself have no target object to resolve.
                object=_object
            )

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        # "object" is a live reference to a scene Object, for local handler use only.
        # It must never reach the wire: it would leak the same private state that
        # Object.json_preprocess strips, and a hand or camera target carries a
        # reference cycle (obj.camera <-> user.hands) that json.dumps cannot encode.
        # The filter runs last, after the merge, so a caller passing
        # object= into json() cannot reintroduce the key either.
        skipped_keys = ["object"]
        json_payload = dict(vars(self))
        json_payload.update(kwargs)
        return {k: v for k, v in json_payload.items() if k not in skipped_keys}

    # TODO (mwfarb): We should standardize this json() transform into BaseObject from Object/Event/Program
    def json(self, **kwargs):
        json_payload = self.json_preprocess(**kwargs)

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
