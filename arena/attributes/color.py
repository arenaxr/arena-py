import re

import webcolors

from .attribute import Attribute


class Color(Attribute):
    """
    Color Attribute.
    Usage: `color=Color(red,green,blue)` or `color=(red,green,blue)`
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
                        wcrgb = webcolors.name_to_rgb("#" + i * "0" + color)
                    except ValueError:
                        break
                if wcrgb is not None:
                    c = (wcrgb.red, wcrgb.green, wcrgb.blue)
                else:
                    c = (128, 128, 128)
            else:
                c = tuple(int(color[c:c + 2], 16) for c in (0, 2, 4))
            self.red, self.green, self.blue = c

        if isinstance(red, (float, int)):
            self.red = int(red)
        if isinstance(blue, (float, int)):
            self.blue = int(blue)
        if isinstance(green, (float, int)):
            self.green = int(green)

        super().__init__(red=self.red, green=self.green, blue=self.blue)

    @property
    def hex(self):
        if isinstance(self.red, str):
            return self.red
        else:
            return f"#{''.join(f'{i:02x}' for i in [self.red, self.green, self.blue])}"
