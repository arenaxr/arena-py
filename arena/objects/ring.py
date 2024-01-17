from .arena_object import Object

class Ring(Object):
    """
    Class for Ring in the ARENA: Ring Geometry
    
    :param float radiusInner: radius inner, defaults to '0.8' (optional)
    :param float radiusOuter: radius outer, defaults to '1.2' (optional)
    :param int segmentsPhi: segments phi, defaults to '10' (optional)
    :param int segmentsTheta: segments theta, defaults to '32' (optional)
    :param float thetaLength: theta length, defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "ring"

    def __init__(self, **kwargs):
        super().__init__(object_type=Ring.object_type, **kwargs)
