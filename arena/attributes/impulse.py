from ..utils import deprecated
from .attribute import Attribute


@deprecated("DEPRECATED: data.impulse is deprecated, use data.physx-force-pushable instead.")
class Impulse(Attribute):
    """
    Impulse attribute class to manage its properties in the ARENA: ***DEPRECATED**: data.impulse is **deprecated**, use data.physx-force-pushable instead.*
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
