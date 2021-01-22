from .arena_object import Object

class Particle(Object):
    """
    Class for Particle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="particle", **kwargs)
