from ..attributes import Position, Rotation
from .arena_object import Object


class Camera(Object):
    """
    Camera object class to manage its properties in the ARENA: Camera is the pose and arena-user component data representing a user avatar.

    :param dict arena_user: arena-user (optional)
    """

    object_type = "camera"

    def __init__(self, object_id, **kwargs):
        data = kwargs.get("data", {})
        arena_user = data.get("arena-user", {})

        self.hasAudio = arena_user.get("hasAudio", False)
        self.hasVideo = arena_user.get("hasVideo", False)
        self.hasAvatar = arena_user.get("hasAvatar", False)
        self.displayName = arena_user.get("displayName", "")
        self.jitsiId = arena_user.get("jitsiId", None)

        self.hands = {}
        self.hand_found_callback = None
        self.hand_remove_callback = None

        position = data.get("position", None)
        rotation = data.get("rotation", None)

        if position is not None and rotation is not None:
            super().__init__(
                object_type=Camera.object_type,
                object_id=object_id,
                position=Position(**position),
                rotation=Rotation(**rotation),
                **kwargs
            )
        elif position is not None:
            super().__init__(
                object_type=Camera.object_type,
                object_id=object_id,
                position=Position(**position),
                **kwargs
            )
        elif rotation is not None:
            super().__init__(
                object_type=Camera.object_type,
                object_id=object_id,
                rotation=Rotation(**rotation),
                **kwargs
            )
