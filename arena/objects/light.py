from .arena_object import Object

class Light(Object):
    """
    Class for Light in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="light", **kwargs)
