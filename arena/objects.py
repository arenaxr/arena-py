from .base_object import *
from .attributes import *
from .utils import *
import uuid

class Object(BaseObject):
    """
    Object class. Defines a generic object in the ARENA.
    """
    all_objects = {} # dict of all objects created so far
    def __init__(self, evt_handler=None, **kwargs):
        # "object_id" is required in kwargs, defaulted to random uuid4
        object_id = kwargs.get("object_id", str(uuid.uuid4()))
        if "object_id" in kwargs: del kwargs["object_id"]

        # "persist" is required in kwargs, defaulted to false
        persist = kwargs.get("persist", False)
        if "persist" in kwargs: del kwargs["persist"]

        # remove "action"
        if "action" in kwargs: del kwargs["action"]

        # special case for "parent"
        if "parent" in kwargs and isinstance(kwargs["parent"], Object):
            kwargs["parent"] = kwargs["parent"].object_id

        # print warning if object is being created with the same id as an existing object
        if Object.exists(object_id):
            print(f"WARNING: an object with object_id of {object_id} was already created. The previous object will be overwritten.")
            Object.remove(Object.get(object_id))

        # setup attributes in the "data" field
        kwargs = kwargs.get("data", kwargs)
        data = Data(**kwargs)
        super().__init__(
                object_id=object_id,
                type="object",
                persist=persist,
                data=data
            )

        self.evt_handler = evt_handler

        # add current object to all_obejcts dict
        Object.add(self)

    def update_attributes(self, evt_handler=None, **kwargs):
        if evt_handler:
            self.evt_handler = evt_handler

        if "data" not in self.__dict__:
            return

        kwargs = kwargs.get("data", kwargs)

        if kwargs is None:
            self.__dict__["data"] = None
            return

        santize_data(kwargs)

        data = self.__dict__["data"]
        for k,v in kwargs.items():
            if (isinstance(v, bool) and v == False) or v is None:
                data[k] = None
                continue

            if k == "position" and not isinstance(v, Position):
                data[k] = Position(**v)
            elif k == "rotation" and not isinstance(v, Rotation):
                data[k] = Rotation(**v)
            elif k == "scale" and not isinstance(v, Scale):
                data[k] = Scale(**v)
            else:
                data[k] = v

    # methods for global object dictionary
    @classmethod
    def get(cls, object_id):
        return Object.all_objects.get(object_id, None)

    @classmethod
    def add(cls, obj):
        object_id = obj.object_id
        Object.all_objects[object_id] = obj

    @classmethod
    def remove(cls, obj):
        object_id = obj.object_id
        del Object.all_objects[object_id]

    @classmethod
    def exists(cls, object_id):
        return object_id in Object.all_objects

class Cube(Object):
    """
    Class for Cube in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="cube", **kwargs)

class Sphere(Object):
    """
    Class for Sphere in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="sphere", **kwargs)

class Circle(Object):
    """
    Class for Circle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="circle", **kwargs)

class Cone(Object):
    """
    Class for Cone in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="cone", **kwargs)

class Cylinder(Object):
    """
    Class for Cylinder in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="cylinder", **kwargs)

class Dodecahedron(Object):
    """
    Class for Dodecahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="dodecahedron", **kwargs)

class Icosahedron(Object):
    """
    Class for Icosahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="icosahedron", **kwargs)

class Tetrahedron(Object):
    """
    Class for Tetrahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="tetrahedron", **kwargs)

class Octahedron(Object):
    """
    Class for Octahedron in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="octahedron", **kwargs)

class Plane(Object):
    """
    Class for Plane in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="plane", **kwargs)

class Ring(Object):
    """
    Class for Ring in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="ring", **kwargs)

class Torus(Object):
    """
    Class for Torus in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="torus", **kwargs)

class TorusKnot(Object):
    """
    Class for TorusKnot in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="torusKnot", **kwargs)

class Triangle(Object):
    """
    Class for Triangle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="triangle", **kwargs)

class GLTF(Object):
    """
    Class for GLTF Model in the ARENA.
    """
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="gltf-model", url=url, **kwargs)

class Image(Object):
    """
    Class for Image in the ARENA.
    """
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="image", url=url, **kwargs)

class Particle(Object):
    """
    Class for Particle in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="particle", **kwargs)

class Text(Object):
    """
    Class for Text in the ARENA.
    [TODO]: update_attribute(text="new text") does get published. maybe a client-side issue?
    """
    def __init__(self, text="placeholder text", **kwargs):
        super().__init__(object_type="text", text=text, **kwargs)

class Light(Object):
    """
    Class for Light in the ARENA.
    """
    def __init__(self, **kwargs):
        super().__init__(object_type="light", **kwargs)

class Line(Object):
    """
    Class for Line in the ARENA.
    """
    def __init__(self, start=Position(0,0,0), end=Position(10,10,10), **kwargs):
        super().__init__(object_type="line", start=start, end=end, **kwargs)

class ThickLine(Object):
    """
    Class for Thickline in the ARENA.
    """
    def __init__(self, path=[Position(0,0,0), Position(10,10,10), Position(10,-10,10)], lineWidth=1, **kwargs):
        #path for thickline is a string for some reason, ie (1,2,3) -> "1 2 3"
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
    """
    Class for Camera in the ARENA.
    """
    def __init__(self, object_id, **kwargs):
        kwargs = kwargs.get("data", kwargs)

        position = kwargs.get("position", None)
        rotation = kwargs.get("rotation", None)

        if position is not None and rotation is not None:
            super().__init__(object_type="camera", object_id=object_id, position=Position(**position), rotation=Rotation(**rotation))
        elif position is not None:
            super().__init__(object_type="camera", object_id=object_id, position=Position(**position))
        elif rotation is not None:
            super().__init__(object_type="camera", object_id=object_id, rotation=Position(**rotation))

