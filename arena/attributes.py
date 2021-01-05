from .base_object import *
from .utils import *
import math
import re
import webcolors
from scipy.spatial.transform import Rotation as R


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
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

    def to_str(self):
        return Utils.tuple_to_string((self.x, self.y, self.z))

    def distance_to(self, pos):
        return math.sqrt((self.x-pos.x)**2 + (self.y-pos.y)**2 + (self.z-pos.z)**2)

class Rotation(Attribute):
    """
    Rotation Attribute in quaternions or euler.
    Usage: rotation=Rotation(x,y,z,w) or rotation=Rotation(x,y,z)
    """
    def __init__(self, x=0, y=0, z=0, w=None):
        if w is not None: # quaternions
            super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=Utils.agran(w))
        else: # euler
            super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z), w=None)

    def __repr__(self):
        if self.is_quaternion:
            return str(vars(self))
        else:
            rot_dict = vars(self).copy()
            del rot_dict["w"]
            return str(rot_dict)

    @property
    def is_quaternion(self):
        return self.w is not None

    @property
    def euler(self):
        if self.is_quaternion: # quaternions
            euler = Rotation.q2e((self.x, self.y, self.z, self.w))
            return Rotation(*euler)
        else: # euler
            return self

    @property
    def quaternion(self):
        if self.is_quaternion: # quaternions
            return self
        else: # euler
            quat = Rotation.e2q((self.x, self.y, self.z))
            return Rotation(*quat)

    @classmethod
    def q2e(cls, q):
        """quaternions to euler"""
        rot = R.from_quat(q)
        return rot.as_euler('xyz', degrees=False)

    @classmethod
    def e2q(cls, e):
        """euler to quaternions"""
        rot = R.from_euler('xyz', e, degrees=False)
        return rot.as_quat()

class Scale(Attribute):
    """
    Scale Attribute.
    Usage: scale=Scale(x,y,z)
    """
    def __init__(self, x=1, y=1, z=1):
        super().__init__(x=Utils.agran(x), y=Utils.agran(y), z=Utils.agran(z))

class Color(Attribute):
    """
    Color Attribute.
    Usage: color=Color(red,green,blue)
    """
    def __init__(self, red=0, green=0, blue=0):
        super().__init__(red=Utils.agran(red), green=Utils.agran(green), blue=Utils.agran(blue))

    @property
    def hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue)

class Animation(Attribute):
    """
    Animation Attribute.
    Usage: animation_mixer=Animation(...)
    """
    def __init__(self, **kwargs):
        if "start" in kwargs:
            kwargs["to"] = kwargs["start"]
            del kwargs["start"]
        if "end" in kwargs:
            kwargs["from"] = kwargs["end"]
            del kwargs["end"]
        super().__init__(**kwargs)

class Sound(Attribute):
    """
    Sound Attribute.
    Usage: sound=Sound(...)
    """
    def __init__(self, positional=False, poolSize=1, src="", **kwargs):
        super().__init__(positional=positional, poolSize=poolSize, src=src, **kwargs)

class Material(Attribute):
    """
    Material Attribute. For setting opacity.
    Usage: material=Material(...)
    """
    def __init__(self, transparent=False, opacity=0, **kwargs):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=Utils.agran(opacity), **kwargs)

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
            force = Utils.tuple_to_string(force)

        if isinstance(position, Position):
            position = position.to_str()
        elif type(position) == tuple or type(position) == list:
            position = Utils.tuple_to_string(position)

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
        dash_words = []
        for k,v in new_data.items():
            # the dashes in these specific keys need to be replaced with underscores
            if k == "goto-url":
                dash_words += [k]
                k = "goto_url"
                if isinstance(v, dict):
                    data[k] = GotoUrl(**v)
                else:
                    data[k] = v

            # this could be called "clickable"
            if k == "click-listener":
                if "clickable" in data:
                    k = "clickable"
                else:
                    dash_words += [k]
                    k = "click_listener"
                data[k] = v

            # this could be called "physics"
            if k == "dynamic-body":
                if "physics" in data:
                    k = "physics"
                else:
                    dash_words += [k]
                    k = "dynamic_body"
                if isinstance(v, dict):
                    data[k] = Physics(**v)
                else:
                    data[k] = v

            # allow user to input tuples, lists, dicts, etc for specific Attributes.
            # everything gets converted to corresponding attribute
            if k == "position" and not isinstance(v, Position):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
                else:
                    data[k] = v

            elif k == "rotation" and not isinstance(v, Rotation):
                if isinstance(v, tuple) or isinstance(v, list):
                    if len(v) == 3:
                        data[k] = Rotation(*v[:3], None)
                    else:
                        data[k] = Rotation(*v[:4])
                elif isinstance(v, dict):
                    # rotation doesnt exist or rotation originally in euler
                    if k not in data or not data[k].is_quaternion:
                        v = Rotation.q2e((v["x"], v["y"], v["z"], v["w"]))
                        data[k] = Rotation(*v)
                    else:
                        data[k] = Rotation(**v)
                else:
                    data[k] = v

            elif k == "scale" and not isinstance(v, Scale):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Scale(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Scale(**v)
                else:
                    data[k] = v

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

        # make False into None
        if (isinstance(v, bool) and v == False) or v is None:
            data[k] = None

        # delete elements with keys that have dashes
        for w in dash_words:
            del data[w]

        return data
