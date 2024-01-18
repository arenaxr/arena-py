from .arena_object import Object

class TorusKnot(Object):
    """
    Class for TorusKnot in the ARENA: Torus Knot Geometry
    
    :param float p: P; defaults to '2' (optional)
    :param float q: Q; defaults to '3' (optional)
    :param float radius: radius; defaults to '1' (optional)
    :param float radiusTubular: radius tubular; defaults to '0.2' (optional)
    :param int segmentsRadial: segments radial; defaults to '8' (optional)
    :param int segmentsTubular: segments tubular; defaults to '100' (optional)
    """
    object_type = "torusKnot"

    def __init__(self, **kwargs):
        super().__init__(object_type=TorusKnot.object_type, **kwargs)
