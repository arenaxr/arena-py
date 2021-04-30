from .arena_object import Object

class Torus(Object):
    """
    Class for Torus in the ARENA.
    """
    object_type = "torus"

    def __init__(self, **kwargs):
        super().__init__(object_type=Torus.object_type, **kwargs)
