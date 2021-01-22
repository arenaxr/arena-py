from .arena_object import Object

class Plane(Object):
    """
    Class for Plane in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="plane", **kwargs)
