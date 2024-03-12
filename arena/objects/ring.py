from .arena_object import Object

class Ring(Object):
    """
    Ring object class to manage its properties in the ARENA: Ring Geometry.

    :param float radiusInner: radius inner Defaults to '0.8' (optional)
    :param float radiusOuter: radius outer Defaults to '1.2' (optional)
    :param int segmentsPhi: segments phi Defaults to '10' (optional)
    :param int segmentsTheta: segments theta Defaults to '32' (optional)
    :param float thetaLength: theta length Defaults to '360' (optional)
    :param float thetaStart: theta start (optional)
    """
    object_type = "ring"

    def __init__(self, **kwargs):
        super().__init__(object_type=Ring.object_type, **kwargs)
