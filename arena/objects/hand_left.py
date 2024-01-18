from .arena_object import Object

class HandLeft(Object):
    """
    Class for HandLeft in the ARENA: Hand is the (left or right) hand metadata pose and controller type of the user avatar.
    
    :param str url: Path to user avatar hand model; defaults to 'static/models/hands/valve_index_left.gltf' (optional)
    :param str dep: Camera object_id this hand belongs to. (optional)
    """
    object_type = "handLeft"

    def __init__(self,**kwargs):
        self.camera = None
        super().__init__(object_type=HandLeft.object_type, **kwargs)
