from .arena_object import Object

class Dodecahedron(Object):
    """
    Dodecahedron object class to manage its properties in the ARENA: Dodecahedron Geometry.

    :param int detail: detail (optional)
    :param float radius: radius Defaults to '1' (optional)
    """
    object_type = "dodecahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Dodecahedron.object_type, **kwargs)
