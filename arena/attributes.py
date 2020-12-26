from .base_object import *
from .utils import *
import math

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
    Rotation Attribute in quaternions.
    Usage: rotation=Rotation(x,y,z,w)
    """
    def __init__(self, x=0, y=0, z=0, w=1):
        super().__init__(x=agran(x), y=agran(y), z=agran(z), w=agran(w))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z, self.w))

class Scale(Attribute):
    """
    Scale Attribute.
    Usage: scale=Scale(x,y,z)
    """
    def __init__(self, x=1, y=1, z=1):
        super().__init__(x=agran(x), y=agran(y), z=agran(z))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z))

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
                continue

            if k == "position" and not isinstance(v, Position):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
            elif k == "rotation" and not isinstance(v, Rotation):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Rotation(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Rotation(**v)
            elif k == "scale" and not isinstance(v, Scale):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Scale(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Scale(**v)
            elif k == "color":
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = rgb_to_hex(v[:3])
                elif isinstance(v, str):
                    data[k] = v
            else:
                try:
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
    def __init__(self, transparent=False, opacity=0):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=opacity)

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
