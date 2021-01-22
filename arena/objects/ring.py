from .arena_object import Object

class Ring(Object):
    """
    Class for Ring in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="ring", **kwargs)
