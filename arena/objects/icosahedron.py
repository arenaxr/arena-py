from .arena_object import Object

class Icosahedron(Object):
    """
    Class for Icosahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="icosahedron", **kwargs)
