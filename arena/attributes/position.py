import math
from collections.abc import Iterable, Mapping

from ..utils import Utils
from .attribute import Attribute


class Position(Attribute):
    """
    Position attribute class to manage its properties in the ARENA: 3D object position.
    Usage: `position=Position(...)` or `position=Position(x,y,z)` or `position=(x,y,z)`

    :param float|Iterable|Mapping x: x Defaults to '0' (optional)
    :param float y: y Defaults to '0' (optional)
    :param float z: z Defaults to '0' (optional)
    """

    def __init__(self, x=None, y=None, z=None):
        if isinstance(x, Mapping):
            if "x" in x and "y" in x and "z" in x:
                x, y, z = x["x"], x["y"], x["z"]
            else:
                raise ValueError("Position takes x,y,z; a 3-element array or list; or a dict with {x,y,z}")
        elif isinstance(x, str):
            if y is None:
                x, y, z = map(float, x.split())
            else:
                raise ValueError("Position takes x,y,z; a 3-element array or list; or a dict with {x,y,z}")
        elif isinstance(x, Iterable):
            if y is None and len(x) == 3:
                x, y, z = x
            else:
                raise ValueError("Position takes x,y,z; a 3-element array or list; or a dict with {x,y,z}")

        x = x or 0
        y = y or 0
        z = z or 0
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    @property
    def array(self):
        return [self.x, self.y, self.z]

    @array.setter
    def array(self, value):
        if not isinstance(value, Iterable) or len(value) != 3 or isinstance(value, Mapping):
            raise ValueError("Position array takes a 3-element array or list")
        self.x = value[0]
        self.y = value[1]
        self.z = value[2]

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))

    def distance_to(self, pos):
        return math.sqrt((self.x - pos.x) ** 2 + (self.y - pos.y) ** 2 + (self.z - pos.z) ** 2)
