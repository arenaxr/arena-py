from .arena_object import Object

class Icosahedron(Object):
    """
    Class for Icosahedron in the ARENA.
    """
    object_type = "icosahedron"

    def __init__(self, **kwargs):
        super().__init__(object_type=Icosahedron.object_type, **kwargs)
