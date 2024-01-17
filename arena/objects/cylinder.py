from .arena_object import Object

class Cylinder(Object):
    """
    Class for Cylinder in the ARENA: cylinder Geometry
    
    :param float height: height, defaults to '1' (optional)
    :param bool openEnded: open ended (optional)
    :param float radius: radius, defaults to '1' (optional)
    :param int segmentsHeight: segments height, defaults to '18' (optional)
    :param int segmentsRadial: segments radial, defaults to '36' (optional)
    :param float thetaLength: theta length, defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "cylinder"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cylinder.object_type, **kwargs)
