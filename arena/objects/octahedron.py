from .arena_object import Object

class Octahedron(Object):
    """
    Class for Octahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="octahedron", **kwargs)
