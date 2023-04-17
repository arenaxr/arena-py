from .arena_object import Object

class Entity(Object):
    """
    Class for Entity in the ARENA.
    """
    object_type = "entity"

    def __init__(self, **kwargs):
        super().__init__(object_type=Entity.object_type, **kwargs)
