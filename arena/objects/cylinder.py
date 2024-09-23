from .arena_object import Object

class Cylinder(Object):
    """
    Cylinder object class to manage its properties in the ARENA: Cylinder Geometry.

    :param float height: height Defaults to '1' (optional)
    :param bool openEnded: open ended Defaults to 'False' (optional)
    :param float radius: radius Defaults to '1' (optional)
    :param int segmentsHeight: segments height Defaults to '18' (optional)
    :param int segmentsRadial: segments radial Defaults to '36' (optional)
    :param float thetaLength: theta length Defaults to '360' (optional)
    :param float thetaStart: theta start Defaults to '0' (optional)
    """
    object_type = "cylinder"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cylinder.object_type, **kwargs)
