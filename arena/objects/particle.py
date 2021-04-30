from .arena_object import Object

class Particle(Object):
    """
    Class for Particle in the ARENA.
    """
    object_type = "particle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Particle.object_type, **kwargs)
