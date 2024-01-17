from .arena_object import Object

class Box(Object):
    """
    Class for Box in the ARENA: Box Geometry
    
    :param float depth: depth, defaults to '1' (optional)
    :param float height: height, defaults to '1' (optional)
    :param int segmentsDepth: segments depth, defaults to '1' (optional)
    :param int segmentsHeight: segments height, defaults to '1' (optional)
    :param int segmentsWidth: segments width, defaults to '1' (optional)
    :param float width: width, defaults to '1' (optional)
    """
    object_type = "box"

    def __init__(self, **kwargs):
        super().__init__(object_type=Box.object_type, **kwargs)
