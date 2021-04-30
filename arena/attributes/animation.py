from ..utils import Utils
from .attribute import Attribute
from .position import Position

class Animation(Attribute):
    """
    Animation Attribute.
    Usage: Animation(...)
    """
    def __init__(self, **kwargs):
        if "start" in kwargs:
            if isinstance(kwargs["start"], tuple) or isinstance(kwargs["start"], list):
                kwargs["start"] = Utils.tuple_to_string(kwargs["start"])
            # can get away with using Position.to_str() even if animation is rotation (euler) or scale
            # since we just want the 3 values to be a space separated string
            elif isinstance(kwargs["start"], Position):
                kwargs["start"] = kwargs["start"].to_str()
        if "end" in kwargs:
            if isinstance(kwargs["end"], tuple) or isinstance(kwargs["end"], list):
                kwargs["end"] = Utils.tuple_to_string(kwargs["end"])
            elif isinstance(kwargs["end"], Position):
                kwargs["end"] = kwargs["end"].to_str()
        super().__init__(**kwargs)
