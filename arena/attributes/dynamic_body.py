from .attribute import Attribute


class DynamicBody(Attribute):
    """
    DynamicBody attribute class to manage its properties in the ARENA: ***DEPRECATED**: data.dynamic-body is **deprecated**, use data.physx-body instead.*
    Usage: `dynamic_body=DynamicBody(...)`

    """

    def __init__(self, type="static", **kwargs):
        _type = type
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type, **kwargs)


class Physics(DynamicBody):
    """
    Alternate name for DynamicBody.
    Usage: `physics=Physics(...)`
    """
