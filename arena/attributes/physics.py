from .attribute import Attribute
from .position import Position

class Physics(Attribute):
    """
    Physics Attribute.
    Usage: physics=Physics(...) OR dynamic_body=Physics(...)
    """
    def __init__(self, type="static"):
        _type = type
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type)
