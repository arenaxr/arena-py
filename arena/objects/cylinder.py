from .arena_object import Object

class Cylinder(Object):
    """
    Class for Cylinder in the ARENA.
    """
    object_type = "cylinder"
    def __init__(self, **kwargs):
        super().__init__(object_type=Cylinder.object_type, **kwargs)
