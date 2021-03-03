from .arena_object import Object

class Octahedron(Object):
    """
    Class for Octahedron in the ARENA.
    """
    object_type = "octahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Octahedron.object_type, **kwargs)
