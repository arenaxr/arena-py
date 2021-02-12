import re
import webcolors
from .attribute import Attribute

class Color(Attribute):
    """
    Color Attribute.
    Usage: color=Color(red,green,blue)
    """
    def __init__(self, red=0, green=0, blue=0):
        if isinstance(red, str):
            # hex to tuple to Color
            color = red.lstrip("#")
            hexcolor = re.search(r"^(?:[0-9a-fA-F]{3}){1,2}$", color)
            if not hexcolor:
                try:
                    wcrgb = webcolors.name_to_rgb(color)
                except:
                    wcrgb = webcolors.hex_to_rgb("#0"+color)
                c = (wcrgb.red, wcrgb.green, wcrgb.blue)
            else:
                c = tuple(int(color[c:c+2], 16) for c in (0, 2, 4))
            red, blue, green = c
        super().__init__(red=red, green=green, blue=blue)

    @property
    def hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)
