from .arena_object import Object

class Triangle(Object):
    """
    Triangle object class to manage its properties in the ARENA: Triangle Geometry
    
    :param dict vertexA: vertex A; defaults to '{'x': 0, 'y': 0.5, 'z': 0}' (optional)
    :param dict vertexB: vertex B; defaults to '{'x': -0.5, 'y': -0.5, 'z': 0}' (optional)
    :param dict vertexC: vertex C; defaults to '{'x': 0.5, 'y': -0.5, 'z': 0}' (optional)
    """
    object_type = "triangle"

    def __init__(self, **kwargs):
        super().__init__(object_type=Triangle.object_type, **kwargs)
