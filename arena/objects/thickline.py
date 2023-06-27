from ..utils import Utils
from .arena_object import Object
from ..attributes import Attribute, Position

class ThickLine(Object):
    """
    Class for ThickLine in the ARENA.
    """
    object_type = "thickline"

    def __init__(self, path=None, lineWidth=1, **kwargs):
        # path for thickline is a string, ie (1,2,3) -> "1 2 3"
        if path is None:
            path = [Position(0, 0, 0), Position(10, 10, 10), Position(10, -10, 10)]
        path_str = ""
        for p in path:
            if isinstance(p, Position):
                p = p.to_str()
            elif isinstance(p, Attribute):
                p = Position(**p.__dict__).to_str()
            elif isinstance(p, tuple) or isinstance(p, list):
                p = Utils.tuple_to_string(p)
            elif isinstance(p, dict):
                p = Position(**p).to_str()
            path_str += p + ","
        path_str = path_str.rstrip(",")
        super().__init__(object_type=ThickLine.object_type, path=path_str, lineWidth=lineWidth, **kwargs)
