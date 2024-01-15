from .arena_object import Object

class HandLeft(Object):
    """
    """
    object_type = "handLeft"

    def __init__(self, **kwargs):
        super().__init__(object_type=HandLeft.object_type, **kwargs)
