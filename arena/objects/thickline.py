from ..utils import Utils
from .arena_object import Object
from ..attributes import Attribute, Position


class Thickline(Object):
    """
    Class for ThickLine in the ARENA.
    """
    object_type = "thickline"

    def __init__(self, **kwargs):
        super().__init__(object_type=Thickline.object_type, **kwargs)


class ThickLine(Thickline):
    """
    Alternate name for Thickline.
    """
