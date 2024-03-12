from .arena_object import Object

class Capsule(Object):
    """
    Capsule object class to manage its properties in the ARENA: Capsule Geometry.

    :param float length: length Defaults to '1' (optional)
    :param float radius: radius Defaults to '1' (optional)
    :param int segmentsCap: segments capsule Defaults to '18' (optional)
    :param int segmentsRadial: segments radial Defaults to '36' (optional)
    """
    object_type = "capsule"

    def __init__(self, **kwargs):
        super().__init__(object_type=Capsule.object_type, **kwargs)
