from .arena_object import Object

class Light(Object):
    """
    Class for Light in the ARENA.
    """
    object_type = "light"

    def __init__(self, **kwargs):
        super().__init__(object_type=Light.object_type, **kwargs)
