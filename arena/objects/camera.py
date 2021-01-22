from .arena_object import Object
from ..attributes import Position, Rotation

class Camera(Object):
    """
    Class for Camera in the ARENA.
    """
    def __init__(self, object_id, **kwargs):
        data = kwargs.get("data", kwargs)

        self.hasAudio = kwargs.get("hasAudio", False)
        self.hasVideo = kwargs.get("hasVideo", False)
        self.hasAvatar = kwargs.get("hasAvatar", False)
        self.displayName = kwargs.get("displayName", "")
        self.jistsiId = kwargs.get("jistsiId", None)

        position = data.get("position", None)
        rotation = data.get("rotation", None)

        if position is not None and rotation is not None:
            super().__init__(object_type="camera", object_id=object_id, position=Position(**position), rotation=Rotation(**rotation), **kwargs)
        elif position is not None:
            super().__init__(object_type="camera", object_id=object_id, position=Position(**position), **kwargs)
        elif rotation is not None:
            super().__init__(object_type="camera", object_id=object_id, rotation=Rotation(**rotation), **kwargs)

    def update_attributes(self, evt_handler=None, **kwargs):
        super().update_attributes(evt_handler=evt_handler, **kwargs)

        self.hasAudio = kwargs.get("hasAudio", False)
        self.hasVideo = kwargs.get("hasVideo", False)
        self.hasAvatar = kwargs.get("hasAvatar", False)
        self.displayName = kwargs.get("displayName", "")
        self.jistsiId = kwargs.get("jistsiId", None)
