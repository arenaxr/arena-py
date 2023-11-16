from ..utils import Utils
from .attribute import Attribute
from collections.abc import Iterable


class Scale(Attribute):
    """
    Scale attribute class to manage its properties in the ARENA: 3D object scale.
    Usage: `scale=Scale(...)` or `scale=Scale(x,y,z)` or `scale=(x,y,z)`

    :param float x: x Defaults to '1' (optional)
    :param float y: y Defaults to '1' (optional)
    :param float z: z Defaults to '1' (optional)
    """

    def __init__(self, x=None, y=None, z=None):
        if x is not None and (y is None or z is None or isinstance(x, Iterable)):
            raise ValueError("Scale takes x,y,z")
        x = x or 1
        y = y or 1
        z = z or 1
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))

    @property
    def array(self):
        return [self.x, self.y, self.z]