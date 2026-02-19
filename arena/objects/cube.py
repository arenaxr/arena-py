from ..utils import deprecated

from .arena_object import Object


@deprecated("Cube (=Box) Geometry (deprecated); Supported for Legacy reasons; Please use Box in new scenes")
class Cube(Object):
    """
    Cube object class to manage its properties in the ARENA: Cube (=Box) Geometry (**deprecated**); Supported for Legacy reasons; Please use Box in new scenes

    :param float depth: *depth* Defaults to '1' (deprecated)
    :param float height: *height* Defaults to '1' (deprecated)
    :param int segmentsDepth: *segments depth* Defaults to '1' (deprecated)
    :param int segmentsHeight: *segments height* Defaults to '1' (deprecated)
    :param int segmentsWidth: *segments width* Defaults to '1' (deprecated)
    :param float width: *width* Defaults to '1' (deprecated)
    """
    object_type = "cube"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cube.object_type, **kwargs)
