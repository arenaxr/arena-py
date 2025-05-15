from .attribute import Attribute


class StaticBody(Attribute):
    """
    StaticBody attribute class to manage its properties in the ARENA: ***DEPRECATED**: data.static-body is **deprecated**, use data.physx-body instead.*
    Usage: `static_body=StaticBody(...)`

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
