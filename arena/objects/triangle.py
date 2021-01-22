from .arena_object import Object

class Triangle(Object):
    """
    Class for Triangle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="triangle", **kwargs)
