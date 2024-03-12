from .arena_object import Object

class Icosahedron(Object):
    """
    Icosahedron object class to manage its properties in the ARENA: Icosahedron Geometry.

    :param int detail: detail (optional)
    :param float radius: radius Defaults to '1' (optional)
    """
    object_type = "icosahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Icosahedron.object_type, **kwargs)
