from .arena_object import Object
from ..attributes import Position

class Line(Object):
    """
    Class for Line in the ARENA.
    """
    object_type = "line"

    def __init__(self, start=(0,0,0), end=(10,10,10), **kwargs):
        super().__init__(object_type=Line.object_type, start=start, end=end, **kwargs)
