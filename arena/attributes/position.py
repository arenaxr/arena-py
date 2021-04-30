import math
from ..utils import Utils
from .attribute import Attribute

class Position(Attribute):
    """
    Position Attribute.
    Usage: position=Position(x,y,z)
    """
    def __init__(self, x=0, y=0, z=0):
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))

    def distance_to(self, pos):
        return math.sqrt((self.x-pos.x)**2 + (self.y-pos.y)**2 + (self.z-pos.z)**2)
