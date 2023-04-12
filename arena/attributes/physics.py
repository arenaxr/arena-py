from .attribute import Attribute

class Physics(Attribute):
    """
    Physics Attribute.
    Usage: physics=Physics(...) OR dynamic_body=Physics(...)
    """
    def __init__(self, type="static", **kwargs):
        _type = type
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type, **kwargs)
