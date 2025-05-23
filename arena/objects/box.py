from .arena_object import Object


class Box(Object):
    """
    Box object class to manage its properties in the ARENA: Box Geometry.

    :param float depth: depth Defaults to '1' (optional)
    :param float height: height Defaults to '1' (optional)
    :param int segmentsDepth: segments depth Defaults to '1' (optional)
    :param int segmentsHeight: segments height Defaults to '1' (optional)
    :param int segmentsWidth: segments width Defaults to '1' (optional)
    :param float width: width Defaults to '1' (optional)
    """
    object_type = "box"

    def __init__(self, **kwargs):
        super().__init__(object_type=Box.object_type, **kwargs)
