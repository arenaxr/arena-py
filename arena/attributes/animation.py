from ..utils import Utils
from .attribute import Attribute
from .position import Position
from .rotation import Rotation
from .scale import Scale

class Animation(Attribute):
    """
    Animation Attribute.
    Usage: Animation(...)
    """
    def __init__(self, **kwargs):
        if "start" in kwargs:
            if isinstance(kwargs["start"], tuple) or isinstance(kwargs["start"], list):
                kwargs["start"] = Utils.tuple_to_string(kwargs["start"])
            elif isinstance(kwargs["start"], (Position, Rotation, Scale)):
                kwargs["start"] = vars(kwargs["start"])
        if "end" in kwargs:
            if isinstance(kwargs["end"], tuple) or isinstance(kwargs["end"], list):
                kwargs["end"] = Utils.tuple_to_string(kwargs["end"])
            elif isinstance(kwargs["end"], (Position, Rotation, Scale)):
                kwargs["end"] = vars(kwargs["end"])
        super().__init__(**kwargs)
