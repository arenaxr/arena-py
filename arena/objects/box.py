from .arena_object import Object

class Box(Object):
    """
    Class for Box in the ARENA.
    """
    object_type = "box"

    def __init__(self, **kwargs):
        super().__init__(object_type=Box.object_type, **kwargs)

class Cube(Object):
    """
    Class for Cube in the ARENA.
    """
    object_type = "cube"

    def __init__(self, **kwargs):
        print("[DEPRECATED]", "Cube(...) will be deprecated soon, please use Box(...) instead!")
        super().__init__(object_type=Cube.object_type, **kwargs)
