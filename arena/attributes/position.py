import math
from ..utils import Utils
from .attribute import Attribute
from collections.abc import Iterable


class Position(Attribute):
    """
    Position attribute class to manage its properties in the ARENA: 3D object position
    Usage: position=Position(...)
    
    :param float x:  (optional)
    :param float y:  (optional)
    :param float z:  (optional)
    """

    def __init__(self, x=None, y=None, z=None):
        if x is not None and (y is None or z is None or isinstance(x, Iterable)):
            raise ValueError("Position takes x,y,z")
        x = x or 0
        y = y or 0
        z = z or 0
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))

    def distance_to(self, pos):
        return math.sqrt(
            (self.x - pos.x) ** 2 + (self.y - pos.y) ** 2 + (self.z - pos.z) ** 2
        )
