from .arena_object import Object

class Dodecahedron(Object):
    """
    Class for Dodecahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="dodecahedron", **kwargs)
