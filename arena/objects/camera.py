from .arena_object import Object
from ..attributes import Position, Rotation

class Camera(Object):
    """
    Class for Camera in the ARENA.
    """
    object_type = "camera"

    def __init__(self, object_id, **kwargs):
        data = kwargs.get("data", kwargs)

        self.hasAudio = data.get("hasAudio", False)
        self.hasVideo = data.get("hasVideo", False)
        self.hasAvatar = data.get("hasAvatar", False)
        self.displayName = data.get("displayName", "")
        self.jistsiId = data.get("jistsiId", None)

        self.hands = {}
        self.hand_found_callback = None
        self.hand_remove_callback = None

        position = data.get("position", None)
        rotation = data.get("rotation", None)

        if position is not None and rotation is not None:
            super().__init__(object_type=Camera.object_type, object_id=object_id, position=Position(**position), rotation=Rotation(**rotation), **kwargs)
        elif position is not None:
            super().__init__(object_type=Camera.object_type, object_id=object_id, position=Position(**position), **kwargs)
        elif rotation is not None:
            super().__init__(object_type=Camera.object_type, object_id=object_id, rotation=Rotation(**rotation), **kwargs)
