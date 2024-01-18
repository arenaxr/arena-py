from .arena_object import Object

class Sphere(Object):
    """
    Class for Sphere in the ARENA: Sphere Geometry
    
    :param float phiLength: phi length; defaults to '360' (optional)
    :param float phiStart: phi start (optional)
    :param float radius: radius; defaults to '1' (optional)
    :param int segmentsHeight: segments height; defaults to '18' (optional)
    :param int segmentsWidth: segments width; defaults to '36' (optional)
    :param float thetaLength: theta length; defaults to '180' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "sphere"

    def __init__(self, **kwargs):
        super().__init__(object_type=Sphere.object_type, **kwargs)
