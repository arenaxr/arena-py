from .arena_object import Object

class Roundedbox(Object):
    """
    Class for Roundedbox in the ARENA: Rounded Box Geometry
    
    :param float depth: depth; defaults to '1' (optional)
    :param float height: height; defaults to '1' (optional)
    :param float width: width; defaults to '1' (optional)
    :param float radius: radius of edge; defaults to '0.15' (optional)
    :param int radiusSegments: segments radius; defaults to '10' (optional)
    """
    object_type = "roundedbox"

    def __init__(self, **kwargs):
        super().__init__(object_type=Roundedbox.object_type, **kwargs)
