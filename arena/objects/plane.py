from .arena_object import Object

class Plane(Object):
    """
    Class for Plane in the ARENA.
    """
    object_type = "plane"

    def __init__(self, **kwargs):
        super().__init__(object_type=Plane.object_type, **kwargs)
