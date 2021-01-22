from .arena_object import Object

class Cone(Object):
    """
    Class for Cone in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="cone", **kwargs)
