from .arena_object import Object


class Ocean(Object):
    """
    Ocean object class to manage its properties in the ARENA: Flat-shaded ocean primitive.

    :param float amplitude: Wave amplitude. Defaults to '0.1' (optional)
    :param float amplitudeVariance: Wave amplitude variance. Defaults to '0.3' (optional)
    :param str color: Wave color. Defaults to '#7AD2F7' (optional)
    :param float density: Density of waves. Defaults to '10' (optional)
    :param float depth: Depth of the ocean area. Defaults to '10' (optional)
    :param float opacity: Wave opacity. Defaults to '0.8' (optional)
    :param float speed: Wave speed. Defaults to '1' (optional)
    :param float speedVariance: Wave speed variance. Defaults to '2' (optional)
    :param float width: Width of the ocean area. Defaults to '10' (optional)
    """
    object_type = "ocean"

    def __init__(self, width=10, depth=10, **kwargs):
        # NOTE: The 'ocean' component for a-frame requires at least depth or width before it will load.
        super().__init__(object_type=Ocean.object_type, width=width, depth=depth, **kwargs)
