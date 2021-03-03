from .arena_object import Object

class Ring(Object):
    """
    Class for Ring in the ARENA.
    """
    object_type = "ring"

    def __init__(self, **kwargs):
        super().__init__(object_type=Ring.object_type, **kwargs)
