from .arena_object import Object

class Cone(Object):
    """
    Class for Cone in the ARENA: Cone Geometry
    
    :param float height: height; defaults to '1' (optional)
    :param bool openEnded: open ended (optional)
    :param float radiusBottom: radius bottom; defaults to '1' (optional)
    :param float radiusTop: radius top; defaults to '0.01' (optional)
    :param int segmentsHeight: segments height; defaults to '18' (optional)
    :param int segmentsRadial: segments radial; defaults to '36' (optional)
    :param float thetaLength: theta length; defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "cone"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cone.object_type, **kwargs)
