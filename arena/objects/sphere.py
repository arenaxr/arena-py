from .arena_object import Object

class Sphere(Object):
    """
    Class for Sphere in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="sphere", **kwargs)
