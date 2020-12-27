from .base_object import *
from .utils import *
import math
import re
import webcolors


class Attribute(BaseObject):
    """
    Attribute class. Defines a generic attribute (ie position, rotation, impulse, etc) in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Position(Attribute):
    """
    Position Attribute.
    Usage: position=Position(x,y,z)
    """
    def __init__(self, x=0, y=0, z=0):
        super().__init__(x=agran(x), y=agran(y), z=agran(z))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z))

    def distance_to(self, pos):
        return math.sqrt((self.x-pos.x)**2 + (self.y-pos.y)**2 + (self.z-pos.z)**2)

class Rotation(Attribute):
    """
    Rotation Attribute in quaternions or euler.
    Usage: rotation=Rotation(x,y,z,w) or rotation=Rotation(x,y,z)
    """
    def __init__(self, x=0, y=0, z=0, w=None):
        if w is not None: # quaternions
            super().__init__(x=agran(x), y=agran(y), z=agran(z), w=agran(w))
        else: # euler
            super().__init__(x=agran(x), y=agran(y), z=agran(z), w=None)

    @property
    def quaternion(self):
        if self.w is not None: # quaternions
            return self
        else: # euler
            quat = e2q((self.x, self.y, self.z))
            return Rotation(*quat)

class Scale(Attribute):
    """
    Scale Attribute.
    Usage: scale=Scale(x,y,z)
    """
    def __init__(self, x=1, y=1, z=1):
        super().__init__(x=agran(x), y=agran(y), z=agran(z))

class Color(Attribute):
    """
    Color Attribute.
    Usage: color=Color(red,green,blue)
    """
    def __init__(self, red=0, green=0, blue=0):
        super().__init__(red=agran(red), green=agran(green), blue=agran(blue))

    @property
    def hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)

class Data(Attribute):
    """
    Data Attribute. Wraps all attributes in JSON.
    """
    def __init__(self, **kwargs):
        data = {}
        data = Data.update_data(data, kwargs)
        super().__init__(**data)

    @classmethod
    def update_data(cls, data, new_data):
        new_data = new_data.get("data", new_data)
        santize_data(new_data)
        for k,v in new_data.items():
            # make False into None
            if (isinstance(v, bool) and v == False) or v is None:
                data[k] = None

            # allow user to input tuples, lists, dicts, etc for specific Attributes
            # everything gets converted to corresponding attribute
            if k == "position" and not isinstance(v, Position):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)

            elif k == "rotation" and not isinstance(v, Rotation):
                if isinstance(v, tuple) or isinstance(v, list):
                    if len(v) == 3:
                        data[k] = Rotation(*v[:3])
                    else:
                        data[k] = Rotation(*v[:4])
                elif isinstance(v, dict):
                    if "w" not in data: # originally in euler
                        v = q2e(v["x"], v["y"], v["z"], v["w"])
                    data[k] = Rotation(**v)

            elif k == "scale" and not isinstance(v, Scale):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Scale(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Scale(**v)

            elif k == "color":
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Color(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Color(**v)
                elif isinstance(v, str):
                    # hex to tuple to Color
                    color = v.lstrip('#')
                    hexcolor = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color)
                    if not hexcolor:
                        wcrgb = webcolors.name_to_rgb(color)
                        v = (wcrgb.red, wcrgb.green, wcrgb.blue)
                    else:
                        v = tuple(int(color[c:c+2], 16) for c in (0, 2, 4))
                    data[k] = Color(*v)

            elif isinstance(v, Attribute):
                data[k] = v

            else:
                try:
                    # unknown attribute
                    data[k] = Attribute(**v)
                except:
                    data[k] = v
        return data

class Animation(Attribute):
    """
    Animation Attribute.
    Usage: animation_mixer=Animation(...)
    """
    def __init__(self, property="rotation", loop=1, dur=1000, **kwargs):
        super().__init__(property=property, loop=loop, dur=dur, **kwargs)

class Sound(Attribute):
    """
    Sound Attribute.
    Usage: sound=Sound(...)
    """
    def __init__(self, positional=False, poolSize=8, autoplay=True, src="", **kwargs):
        super().__init__(positional=positional, poolSize=poolSize, autoplay=autoplay, src=src, **kwargs)

class Material(Attribute):
    """
    Material Attribute. For setting opacity.
    Usage: material=Material(...)
    """
    def __init__(self, transparent=False, opacity=0, **kwargs):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=opacity, **kwargs)

class GotoUrl(Attribute):
    """
    GotoUrl Attribute.
    Usage: goto_url=GotoUrl(...)
    """
    def __init__(self, dest="static", on="mousedown", url=""):
        if dest != "popup" and dest != "newtab" and dest != "sametab":
            dest = "popup"
        super().__init__(dest=dest, on=on, url=url)

class Impulse(Attribute):
    """
    Impulse Attribute.
    Usage: impulse=Impulse(...)
    """
    def __init__(self, on="mousedown", force=Position(0,0,0), position=Position(0,0,0)):
        if isinstance(force, Position):
            force = force.to_str()
        elif type(force) == tuple or type(force) == list:
            force = tuple_to_string(force)

        if isinstance(position, Position):
            position = position.to_str()
        elif type(position) == tuple or type(position) == list:
            position = tuple_to_string(position)

        super().__init__(on=on, force=force, position=position)

class Physics(Attribute):
    """
    Physics Attribute.
    Usage: physics=Physics(...) OR dynamic_body=Physics(...)
    """
    def __init__(self, type="static"):
        _type = type
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type)
