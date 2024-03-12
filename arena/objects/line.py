from .arena_object import Object
from ..attributes import Position

class Line(Object):
    """
    Line object class to manage its properties in the ARENA: Draw a line.

    :param str color: Line color. Defaults to '#74BEC1' (optional)
    :param dict end: End coordinate. Defaults to '{'x': -0.5, 'y': -0.5, 'z': 0}' (optional)
    :param float opacity: Line opacity. Defaults to '1' (optional)
    :param dict start: Start point coordinate. Defaults to '{'x': 0, 'y': 0.5, 'z': 0}' (optional)
    :param bool visible: Whether the material is visible. Defaults to 'True' (optional)
    """
    object_type = "line"

    def __init__(self, start=(0,0,0), end=(10,10,10), **kwargs):
        super().__init__(object_type=Line.object_type, start=start, end=end, **kwargs)
