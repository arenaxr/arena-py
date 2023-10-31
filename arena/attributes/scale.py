from ..utils import Utils
from .attribute import Attribute
from collections.abc import Iterable


class Scale(Attribute):
    """
    Scale Attribute.
    Usage: scale=Scale(x,y,z)
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
