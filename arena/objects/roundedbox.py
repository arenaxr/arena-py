from .arena_object import Object

class Roundedbox(Object):
    """
    Roundedbox object class to manage its properties in the ARENA: Rounded Box Geometry.

    :param float depth: depth Defaults to '1' (optional)
    :param float height: height Defaults to '1' (optional)
    :param float radius: radius of edge Defaults to '0.15' (optional)
    :param int radiusSegments: segments radius Defaults to '10' (optional)
    :param float width: width Defaults to '1' (optional)
    """
    object_type = "roundedbox"

    def __init__(self, **kwargs):
        super().__init__(object_type=Roundedbox.object_type, **kwargs)
