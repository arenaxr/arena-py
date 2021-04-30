from ..utils import Utils
from .attribute import Attribute

class Scale(Attribute):
    """
    Scale Attribute.
    Usage: scale=Scale(x,y,z)
    """
    def __init__(self, x=1, y=1, z=1):
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))
