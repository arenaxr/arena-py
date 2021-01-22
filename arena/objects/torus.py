from .arena_object import Object

class Torus(Object):
    """
    Class for Torus in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="torus", **kwargs)
