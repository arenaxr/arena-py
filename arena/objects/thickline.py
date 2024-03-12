from ..utils import Utils
from .arena_object import Object
from ..attributes import Attribute, Position

class Thickline(Object):
    """
    Thickline object class to manage its properties in the ARENA: Draw a line that can have a custom width.

    :param str color: Line color. Defaults to '#000000' (optional)
    :param float lineWidth: Width of line in px. Defaults to '1' (optional)
    :param str lineWidthStyler: Allows defining the line width as a function of relative position p along the path of the line. By default it is set to a constant 1. You may also choose one of the preset functions. Allows [default, grow, shrink, center-sharp, center-smooth, sine-wave] Defaults to 'default' (optional)
    :param str path: Comma-separated list of x y z coordinates of the line vertices. Defaults to '-2 -1 0, 0 20 0, 10 -1 10' (optional)
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


class ThickLine(Thickline):
    """
    Alternate name for Thickline.
    """
