from .arena_object import Object

class Ocean(Object):
    """
    Ocean object class to manage its properties in the ARENA: Flat-shaded ocean primitive.
    
    :param float amplitude: Wave amplitude.; defaults to '0.1' (optional)
    :param float amplitudeVariance: Wave amplitude variance.; defaults to '0.3' (optional)
    :param str color: Wave color.; defaults to '#7AD2F7' (optional)
    :param float density: Density of waves.; defaults to '10' (optional)
    :param float depth: Depth of the ocean area.; defaults to '10' (optional)
    :param float opacity: Wave opacity.; defaults to '0.8' (optional)
    :param float speed: Wave speed.; defaults to '1' (optional)
    :param float speedVariance: Wave speed variance.; defaults to '2' (optional)
    :param float width: Width of the ocean area.; defaults to '10' (optional)
    """
    object_type = "ocean"

    def __init__(self, **kwargs):
        super().__init__(object_type=Ocean.object_type, **kwargs)
