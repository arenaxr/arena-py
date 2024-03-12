from .arena_object import Object

class Octahedron(Object):
    """
    Octahedron object class to manage its properties in the ARENA: Octahedron Geometry.

    :param int detail: detail (optional)
    :param float radius: radius Defaults to '1' (optional)
    """
    object_type = "octahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Octahedron.object_type, **kwargs)
