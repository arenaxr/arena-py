from .arena_object import Object

class Cone(Object):
    """
    Class for Cone in the ARENA.
    """
    object_type = "cone"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cone.object_type, **kwargs)
