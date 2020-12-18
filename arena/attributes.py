from base_object import *
from utils import *

class Attribute(BaseObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Data(Attribute):
    def __init__(self, **kwargs):
        # replace underscores in data with dashes for aframe attributes
        underscore_words = []
        for k,v in kwargs.items():
            if "_" in k and k != "object_type":
                underscore_words += [k]
        for w in underscore_words:
            v = kwargs[w]
            kwargs[w.replace("_", "-")] = v
            del kwargs[w]
        super().__init__(**kwargs)

class Position(Attribute):
    def __init__(self, x=0, y=0, z=0):
        super().__init__(x=agran(x), y=agran(y), z=agran(z))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z))

class Rotation(Attribute):
    def __init__(self, x=0, y=0, z=0, w=1):
        super().__init__(x=agran(x), y=agran(y), z=agran(z), w=agran(w))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z, self.w))

class Scale(Attribute):
    def __init__(self, x=1, y=1, z=1):
        super().__init__(x=agran(x), y=agran(y), z=agran(z))

    def to_str(self):
        return tuple_to_string((self.x, self.y, self.z))

class Animation(Attribute):
    def __init__(self, clip=False, loop=0, repetitions=0, timeScale=0):
        super().__init__(clip=clip, loop=loop, repetitions=repetitions, timeScale=timeScale)

class Material(Attribute):
    def __init__(self, transparent=False, opacity=0):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=opacity)

class Impulse(Attribute):
    def __init__(self, on=True, force=Position(0,0,0), position=Position(0,0,0)):
        if type(force) == Position:
            force = force.to_str()
        elif type(force) == tuple or type(force) == list:
            force = tuple_to_string(force)

        if type(position) == Position:
            position = position.to_str()
        elif type(position) == tuple or type(position) == list:
            position = tuple_to_string(position)

        super().__init__(on=on, force=force, position=position)

class Physics(Attribute):
    def __init__(self, type="static"):
        if type != "static" or type != "dynamic":
            type = "none"
        super().__init__(type=type)
