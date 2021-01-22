from .arena_object import Object

class Box(Object):
    """
    Class for Box in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="box", **kwargs)

class Cube(Object):
    """
    Class for Cube in the ARENA.
    """
    def __init__(self, **kwargs):
        print("[WARNING]", "Cube will be deprecated soon, please use Box instead!")
        super().__init__(object_type="cube", **kwargs)
