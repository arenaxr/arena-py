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
        replace_underscores(kwargs)

        # handle special case where "physics" should be "dynamic-body"
        if "physics" in kwargs:
            ref = kwargs["physics"]
            del kwargs["physics"]
            kwargs["dynamic-body"] = ref

        super().__init__(**kwargs)

class AnimationMixer(Attribute):
    """
    AnimationMixer Attribute.
    Usage: animation_mixer=AnimationMixer(...)
    """
    def __init__(self, clip=False, loop=0, repetitions=0, timeScale=0):
        super().__init__(clip=clip, loop=loop, repetitions=repetitions, timeScale=timeScale)

class Sound(Attribute):
    """
    Sound Attribute.
    Usage: sound=Sound(...)
    """
    def __init__(self, positional=False, poolSize=8, autoplay=True, src=""):
        super().__init__(positional=positional, poolSize=poolSize, autoplay=autoplay, src=src)

class Material(Attribute):
    """
    Material Attribute. For setting opacity.
    Usage: material=Material(...)
    """
    def __init__(self, transparent=False, opacity=0):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=opacity)

class Impulse(Attribute):
    """
    Impulse Attribute.
    [TODO] this does not work in the browser!
    Usage: impulse=Impulse(...)
    """
    def __init__(self, on=True, force=Position(0,0,0), position=Position(0,0,0)):
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
    [TODO] this does not work in the browser!
    Usage: physics=Physics(...) OR dynamic_body=Physics(...)
    """
    def __init__(self, _type="static"):
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type)
