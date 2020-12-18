from base_object import *
from attributes import *
from utils import *
import uuid

class Object(BaseObject):
    all_objects = {}
    def __init__(self,
                object_id = str(uuid.uuid4()),
                object_type = "cube",
                position = Position(0,0,0),
                rotation = Rotation(0,0,0,1),
                scale = Scale(1,1,1),
                color = "#000000",
                persist = False,
                callback = None,
                **kwargs
            ):

        if Object.exists(object_id):
            print(f"WARNING: an object with object_id of {object_id} was already created. The previous object has been overwritten.")

        if "data" in kwargs:
            kwargs = kwargs["data"]
        data = Data(
                object_type=object_type,
                position=position,
                rotation=rotation,
                scale=scale,
                color=color,
                **kwargs
            )
        super().__init__(
                object_id=object_id,
                type="object",
                persist=persist,
                data=data
            )
        self.callback = callback

        Object.add(self)

    def update_attributes(self, **kwargs):
        if "data" not in self.__dict__:
            return

        if "data" in kwargs:
            kwargs = kwargs["data"]

        if kwargs is None:
            self.__dict__["data"] = None
            return

        data = self.__dict__["data"]
        for k,v in kwargs.items():
            if k in vars(data):
                data[k] = None if not v else v

    # methods for global object dictionary
    @classmethod
    def add(self, obj):
        object_id = obj.object_id
        Object.all_objects[object_id] = obj

    @classmethod
    def remove(self, obj):
        object_id = obj.object_id
        del Object.all_objects[object_id]

    @classmethod
    def exists(self, object_id):
        return object_id in Object.all_objects

class Cube(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="cube", **kwargs)

class Sphere(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="sphere", **kwargs)

class Circle(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="circle", **kwargs)

class Cone(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="cone", **kwargs)

class Cylinder(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="cylinder", **kwargs)

class Dodecahedron(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="dodecahedron", **kwargs)

class Icosahedron(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="icosahedron", **kwargs)

class Tetrahedron(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="tetrahedron", **kwargs)

class Octahedron(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="octahedron", **kwargs)

class Plane(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="plane", **kwargs)

class Ring(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="ring", **kwargs)

class Torus(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="torus", **kwargs)

class TorusKnot(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="torusKnot", **kwargs)

class Triangle(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="triangle", **kwargs)

class GLTF(Object):
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="gltf-model", url=url, **kwargs)

class Image(Object):
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="image", url=url, **kwargs)

class Particle(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="particle", **kwargs)

class Text(Object):
    def __init__(self, text="placeholder text", **kwargs):
        super().__init__(object_type="text", text=text, **kwargs)

class Light(Object):
    def __init__(self, **kwargs):
        super().__init__(object_type="light", **kwargs)

class Line(Object):
    def __init__(self, start=Position(0,0,0), end=Position(10,10,10), **kwargs):
        super().__init__(object_type="line", start=start, end=end, **kwargs)

class ThickLine(Object):
    def __init__(self, path=[Position(0,0,0), Position(10,10,10), Position(10,-10,10)], lineWidth=1, **kwargs):
        path_str = ""
        for p in path:
            if type(p) == Position:
                p = p.to_str()
            elif type(p) == tuple or type(p) == list:
                p = tuple_to_string(p)
            path_str += p + ","
        path_str = path_str.rstrip(",")
        super().__init__(object_type="thickline", path=path_str, lineWidth=lineWidth, **kwargs)

class Camera(Object):
    def __init__(self, object_id, **kwargs):
        super().__init__(object_type="camera", object_id=object_id)
