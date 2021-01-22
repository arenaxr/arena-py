from .arena_object import Object

class Circle(Object):
    """
    Class for Circle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="circle", **kwargs)
