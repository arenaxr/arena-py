from .arena_object import Object

class Circle(Object):
    """
    Circle object class to manage its properties in the ARENA: Circle Geometry.

    :param float radius: radius Defaults to '1' (optional)
    :param int segments: segments Defaults to '32' (optional)
    :param float thetaLength: theta length Defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "circle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Circle.object_type, **kwargs)
