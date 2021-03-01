from ..attributes import Attribute
from .arena_object import Object

class Landmarks(Object):
    """Landmarks class. Holds a list of landmarks."""
    def __init__(self):
        super().__init__(object_id="scene-landmarks", persist=True)
        self.type = "landmarks" # force type to be "landmarks"
        self.data.landmarks = []

    def add(self, obj, label):
        if isinstance(obj, Attribute):
            object_id = obj.object_id
        else:
            object_id = obj
        self.data.landmarks += [{
            "object_id": object_id,
            "label": label
        }]
