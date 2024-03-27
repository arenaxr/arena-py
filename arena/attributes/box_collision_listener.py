from .attribute import Attribute


class BoxCollisionListener(Attribute):
    """
    BoxCollisionListener attribute class to manage its properties in the ARENA: Listen for bounding-box collisions with user camera and hands. Must be applied to an object or model with geometric mesh. Collisions are determined by course bounding-box overlaps.
    Usage: `box_collision_listener=BoxCollisionListener(...)`

    :param bool dynamic: Set true for a moving object, which should have its bounding box recalculated regularly to determine proper collision. (optional)
    :param bool enabled: Publish detections, set `false` to disable. Defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
