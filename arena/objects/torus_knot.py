from .arena_object import Object

class TorusKnot(Object):
    """
    Class for TorusKnot in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="torusKnot", **kwargs)
