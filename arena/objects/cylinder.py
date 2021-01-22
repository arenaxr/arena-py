from .arena_object import Object

class Cylinder(Object):
    """
    Class for Cylinder in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="cylinder", **kwargs)
