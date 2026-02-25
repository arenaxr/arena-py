from ..utils import deprecated
from .attribute import Attribute


@deprecated("DEPRECATED: data.static-body is deprecated, use data.physx-body instead.")
class StaticBody(Attribute):
    """
    StaticBody attribute class to manage its properties in the ARENA: ***DEPRECATED**: data.static-body is **deprecated**, use data.physx-body instead.*
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
