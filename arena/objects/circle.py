from .arena_object import Object

class Circle(Object):
    """
    Class for Circle in the ARENA.
    """
    object_type = "circle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Circle.object_type, **kwargs)
