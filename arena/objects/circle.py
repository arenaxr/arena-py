from .arena_object import Object

class Circle(Object):
    """
    Class for Circle in the ARENA: Circle Geometry
    
    :param float radius: radius, defaults to '1' (optional)
    :param int segments: segments, defaults to '32' (optional)
    :param float thetaLength: theta length, defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "circle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Circle.object_type, **kwargs)
