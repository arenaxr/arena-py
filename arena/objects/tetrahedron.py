from .arena_object import Object

class Tetrahedron(Object):
    """
    Class for Tetrahedron in the ARENA: Tetrahedron Geometry
    
    :param int detail: detail (optional)
    :param float radius: radius, defaults to '1' (optional)
    """
    object_type = "tetrahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Tetrahedron.object_type, **kwargs)
