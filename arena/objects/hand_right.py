from .arena_object import Object

class HandRight(Object):
    """
    HandRight object class to manage its properties in the ARENA: Hand is the (left or right) hand metadata pose and controller type of the user avatar.

    :param str dep: Camera object_id this hand belongs to. Defaults to '' (optional)
    :param str url: Path to user avatar hand model. Defaults to 'static/models/hands/valve_index_left.gltf' (optional)
    """
    object_type = "handRight"

    def __init__(self,**kwargs):
        self.camera = None
        super().__init__(object_type=HandRight.object_type, **kwargs)
