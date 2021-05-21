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
            wcrgb = None
            if not hexcolor:
                # try appending leading zeros until it works
                for i in range(8):
                    try:
                        wcrgb = webcolors.name_to_rgb("#"+i*"0"+color)
                    except:
                        break
                if wcrgb is not None:
                    c = (wcrgb.red, wcrgb.green, wcrgb.blue)
                else:
                    c = (128,128,128)
            else:
                c = tuple(int(color[c:c+2], 16) for c in (0, 2, 4))
            red, green, blue = c
        super().__init__(red=red, green=green, blue=blue)

    @property
    def hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)
