from ..utils import deprecated
from .attribute import Attribute


@deprecated("DEPRECATED: data.dynamic-body is deprecated, use data.physx-body instead.")
class DynamicBody(Attribute):
    """
    DynamicBody attribute class to manage its properties in the ARENA: ***DEPRECATED**: data.dynamic-body is **deprecated**, use data.physx-body instead.*
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@deprecated("DEPRECATED: Physics is deprecated, use PhysxBody instead.")
class Physics(DynamicBody):
    """
    Alternate name for DynamicBody.
    Usage: `physics=Physics(...)`
    """
