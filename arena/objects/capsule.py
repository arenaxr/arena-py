from .arena_object import Object

class Capsule(Object):
    """
    Class for Capsule in the ARENA: Capsule Geometry
    
    :param float length: length, defaults to '1' (optional)
    :param float radius: radius, defaults to '1' (optional)
    :param int segmentsCap: segments capsule, defaults to '18' (optional)
    :param int segmentsRadial: segments radial, defaults to '36' (optional)
    """
    object_type = "capsule"

    def __init__(self, **kwargs):
        super().__init__(object_type=Capsule.object_type, **kwargs)
