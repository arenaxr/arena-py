from .arena_object import Object

class HandRight(Object):
    """
    Class for Right Hands/Controllers in the ARENA.
    """
    object_type = "handRight"

    def __init__(self,**kwargs):
        self.camera = None
        super().__init__(object_type=HandRight.object_type, **kwargs)
