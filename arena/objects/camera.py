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

        # Collect the pose kwargs first, then call super() exactly once. A
        # super() call per pose combination left the "neither" case -- which is
        # the shape an arena-user-only update takes -- with no super() call at
        # all, and so no object_id, no data, and no entry in all_objects. With a
        # single call site that gap cannot come back.
        pose = {}
        if position is not None:
            pose["position"] = Position(**position)
        if rotation is not None:
            pose["rotation"] = Rotation(**rotation)

        super().__init__(
            object_type=Camera.object_type,
            object_id=object_id,
            **pose,
            **kwargs
        )
