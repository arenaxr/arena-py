from .arena_object import Object

class Box(Object):
    """
    Class for Box in the ARENA.
    """
    object_type = "box"

    def __init__(self, **kwargs):
        super().__init__(object_type=Box.object_type, **kwargs)
