from .attribute import Attribute

class Color(Attribute):
    """
    Color Attribute.
    Usage: color=Color(red,green,blue)
    """
    def __init__(self, red=0, green=0, blue=0):
        super().__init__(red=red, green=green, blue=blue)

    @property
    def hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)
