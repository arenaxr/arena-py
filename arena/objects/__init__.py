from .arena_object import Object
from .box import Box
from .camera import Camera
from .circle import Circle
from .cone import Cone
from .cylinder import Cylinder
from .dodecahedron import Dodecahedron
from .gltf import GLTF
from .icosahedron import Icosahedron
from .hands import HandLeft, HandRight
from .image import Image
from .light import Light
from .line import Line
from .octahedron import Octahedron
from .plane import Plane
from .ring import Ring
from .sphere import Sphere
from .tetrahedron import Tetrahedron
from .text import Text
from .thickline import ThickLine
from .torus import Torus
from .torus_knot import TorusKnot
from .triangle import Triangle
from .ui import *

OBJECT_TYPE_MAP = {
    Box.object_type:          Box,
    Camera.object_type:       Camera,
    Circle.object_type:       Circle,
    Cone.object_type:         Cone,
    Box.object_type:          Box,
    Cylinder.object_type:     Cylinder,
    Dodecahedron.object_type: Dodecahedron,
    Object.object_type:       Object,
    GLTF.object_type:         GLTF,
    Icosahedron.object_type:  Icosahedron,
    Image.object_type:        Image,
    HandLeft.object_type:     HandLeft,
    HandRight.object_type:    HandRight,
    Light.object_type:        Light,
    Line.object_type:         Line,
    Object.object_type:       Object,
    Octahedron.object_type:   Octahedron,
    Plane.object_type:        Plane,
    Ring.object_type:         Ring,
    Sphere.object_type:       Sphere,
    Tetrahedron.object_type:  Tetrahedron,
    Text.object_type:         Text,
    ThickLine.object_type:    ThickLine,
    Torus.object_type:        Torus,
    TorusKnot.object_type:    TorusKnot,
    Triangle.object_type:     Triangle,
}
