from .arena_object import Object

class Plane(Object):
    """
    Plane object class to manage its properties in the ARENA: Plane Geometry
    
    :param float height: height; defaults to '1' (optional)
    :param int segmentsHeight: segments height; defaults to '1' (optional)
    :param int segmentsWidth: segments width; defaults to '1' (optional)
    :param float width: width; defaults to '1' (optional)
    """
    object_type = "plane"

    def __init__(self, **kwargs):
        super().__init__(object_type=Plane.object_type, **kwargs)
