from .arena_object import Object

class Cone(Object):
    """
    Cone object class to manage its properties in the ARENA: Cone Geometry.

    :param float height: height Defaults to '1' (optional)
    :param bool openEnded: open ended (optional)
    :param float radiusBottom: radius bottom Defaults to '1' (optional)
    :param float radiusTop: radius top Defaults to '0.01' (optional)
    :param int segmentsHeight: segments height Defaults to '18' (optional)
    :param int segmentsRadial: segments radial Defaults to '36' (optional)
    :param float thetaLength: theta length Defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "cone"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cone.object_type, **kwargs)
