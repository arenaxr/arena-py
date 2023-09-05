from .arena_object import Object

class HandLeft(Object):
    """
    Class for Left Hands/Controllers in the ARENA.
    """
    object_type = "handLeft"

    def __init__(self,**kwargs):
        self.camera = None
        super().__init__(object_type=HandLeft.object_type, **kwargs)

class HandRight(Object):
    """
    Class for Right Hands/Controllers in the ARENA.
    """
    object_type = "handRight"

    def __init__(self,**kwargs):
        self.camera = None
        super().__init__(object_type=HandRight.object_type, **kwargs)
