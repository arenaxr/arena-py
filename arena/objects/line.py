from .arena_object import Object
from ..attributes import Position

class Line(Object):
    """
    Class for Line in the ARENA.
    """
    object_type = "line"

    def __init__(self, start, end, **kwargs):
        super().__init__(object_type=Line.object_type, start=start, end=end, **kwargs)

