from .arena_object import Object

class Triangle(Object):
    """
    Class for Triangle in the ARENA.
    """
    object_type = "triangle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Triangle.object_type, **kwargs)
