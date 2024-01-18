from .arena_object import Object

class Dodecahedron(Object):
    """
    Class for Dodecahedron in the ARENA: dodecahedron Geometry
    
    :param int detail: detail (optional)
    :param float radius: radius; defaults to '1' (optional)
    """
    object_type = "dodecahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Dodecahedron.object_type, **kwargs)
