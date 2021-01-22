from .arena_object import Object

class Tetrahedron(Object):
    """
    Class for Tetrahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="tetrahedron", **kwargs)
