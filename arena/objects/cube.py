from ..utils import deprecated
from .arena_object import Object


@deprecated("Cube (=Box) Geometry (deprecated); Supported for Legacy reasons; Please use Box in new scenes")
class Cube(Object):
    """
    Cube object class to manage its properties in the ARENA: Cube (=Box) Geometry (**deprecated**); Supported for Legacy reasons; Please use Box in new scenes
    """
    object_type = "cube"

    def __init__(self, **kwargs):
        super().__init__(object_type=Cube.object_type, **kwargs)
