from ..utils import Utils
from .attribute import Attribute
from .position import Position

class Landmark(Attribute):
    """
    Landmark Attribute.
    Usage: Animation(...)
    """
    def __init__(self, **kwargs):
        if "offsetPosition" in kwargs:
            if isinstance(kwargs["offsetPosition"], tuple) or isinstance(kwargs["offsetPosition"], list):
                kwargs["offsetPosition"] = Utils.tuple_to_string(kwargs["offsetPosition"])
            # can get away with using Position.to_str() even if animation is rotation (euler) or scale
            # since we just want the 3 values to be a space separated string
            elif isinstance(kwargs["offsetPosition"], Position):
                kwargs["offsetPosition"] = kwargs["offsetPosition"].to_str()
        super().__init__(**kwargs)
