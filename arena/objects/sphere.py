from .arena_object import Object

class Sphere(Object):
    """
    Class for Sphere in the ARENA.
    """
    object_type = "sphere"

    def __init__(self, **kwargs):
        super().__init__(object_type=Sphere.object_type, **kwargs)
