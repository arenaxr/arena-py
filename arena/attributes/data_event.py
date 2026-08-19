from ..utils import *
from .attribute import Attribute
from .position import Position


class DataEvent(Attribute):
    def __init__(self, **kwargs):
        data = {}
        data = DataEvent.update_data(data, kwargs)
        super().__init__(**data)

    @classmethod
    def update_data(cls, data, new_data):
        new_data = new_data.get("data", new_data)
        for k, v in new_data.items():

            # An Arena Object must never be stored in event data. Event.json()
            # serializes every data key straight out of vars(), so a stored Object
            # rides onto the wire carrying the private state Object.json_preprocess
            # exists to strip, and a camera- or hand-shaped value does not even get
            # that far: obj.camera <-> user.hands is a real cycle, so json.dumps
            # raises "Circular reference detected" at publish time instead. Data
            # refuses the same thing for scene data; this is the event-data half.
            #
            # Decided by class name over the MRO, a crude check that avoids a
            # circular import of Arena Object. Unlike Data's first-base-only check
            # this also catches Object itself and subclasses nested deeper than one
            # level (Model, GLTF, Card, ButtonPanel, Prompt, ThickLine).
            #
            # No key is exempt: Data exempts "parent" because a scene object
            # legitimately takes one, while event data has no parent semantics and
            # no caller in the library passes an Object through event data - Scene's
            # event builders all reduce an Object to its object_id first. object_id
            # is read defensively because Camera.__init__ skips super().__init__
            # when its data carries no pose, leaving no object_id to report.
            if any(base.__name__ == "Object" for base in type(v).__mro__):
                raise ValueError(
                    f"Invalid Arena Object as attribute {k}: "
                    f"{getattr(v, 'object_id', type(v).__name__)}"
                )

            # allow user to input tuples, lists, dicts, etc for specific Attributes.
            # everything gets converted to corresponding attribute
            if (k == "originPosition" or k == "targetPosition") and not isinstance(v, Position):
                if isinstance(v, (list, tuple)):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
                else:
                    data[k] = v

            elif isinstance(v, Attribute):
                data[k] = v

            else:
                try:
                    # unknown attribute
                    data[k] = Attribute(**v)
                except:
                    data[k] = v

        return data

    @property
    @deprecated("DEPRECATED: data.source is deprecated for clientEvent, use data.target instead.")
    def source(self):
        return None

    @source.setter
    @deprecated("DEPRECATED: data.source is deprecated for clientEvent, use data.target instead.")
    def source(self, value):
        return

    @property
    @deprecated("DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead.")
    def clickPos(self):
        return None

    @clickPos.setter
    @deprecated("DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead.")
    def clickPos(self, value):
        return

    @property
    @deprecated("DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead.")
    def position(self):
        return None

    @position.setter
    @deprecated("DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead.")
    def position(self, value):
        return
