from .arena_object import Object

class Torus(Object):
    """
    Torus object class to manage its properties in the ARENA: Torus Geometry
    
    :param float arc: Arc; defaults to '360' (optional)
    :param float radius: radius; defaults to '1' (optional)
    :param float radiusTubular: radius tubular; defaults to '0.2' (optional)
    :param int segmentsRadial: segments radial; defaults to '36' (optional)
    :param int segmentsTubular: segments tubular; defaults to '32' (optional)
    """
    object_type = "torus"

    def __init__(self, **kwargs):
        super().__init__(object_type=Torus.object_type, **kwargs)
