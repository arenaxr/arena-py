from .arena_object import Object

class TorusKnot(Object):
    """
    TorusKnot object class to manage its properties in the ARENA: Torus Knot Geometry.

    :param float p: P Defaults to '2' (optional)
    :param float q: Q Defaults to '3' (optional)
    :param float radius: radius Defaults to '1' (optional)
    :param float radiusTubular: radius tubular Defaults to '0.2' (optional)
    :param int segmentsRadial: segments radial Defaults to '8' (optional)
    :param int segmentsTubular: segments tubular Defaults to '100' (optional)
    """
    object_type = "torusKnot"

    def __init__(self, **kwargs):
        super().__init__(object_type=TorusKnot.object_type, **kwargs)
