from .arena_object import Object

class Sphere(Object):
    """
    Sphere object class to manage its properties in the ARENA: Sphere Geometry.

    :param float phiLength: phi length Defaults to '360' (optional)
    :param float phiStart: phi start (optional)
    :param float radius: radius Defaults to '1' (optional)
    :param int segmentsHeight: segments height Defaults to '18' (optional)
    :param int segmentsWidth: segments width Defaults to '36' (optional)
    :param float thetaLength: theta length Defaults to '180' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "sphere"

    def __init__(self, **kwargs):
        super().__init__(object_type=Sphere.object_type, **kwargs)
