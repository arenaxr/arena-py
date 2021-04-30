from .arena_object import Object

class TorusKnot(Object):
    """
    Class for TorusKnot in the ARENA.
    """
    object_type = "torusKnot"

    def __init__(self, **kwargs):
        super().__init__(object_type=TorusKnot.object_type, **kwargs)
