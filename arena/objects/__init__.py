from .box import Box
from .camera import Camera
from .circle import Circle
from .cone import Cone
from .cylinder import Cylinder
from .dodecahedron import Dodecahedron
from .gltf import GLTF
from .icosahedron import Icosahedron
from .image import Image
from .landmarks import Landmarks
from .light import Light
from .line import Line
from .arena_object import Object
from .octahedron import Octahedron
from .particle import Particle
from .plane import Plane
from .ring import Ring
from .sphere import Sphere
from .tetrahedron import Tetrahedron
from .text import Text
from .thickline import ThickLine
from .torus import Torus
from .torus_knot import TorusKnot
from .triangle import Triangle

OBJECT_TYPE_MAP = {
    "box": Box,
    "cube": Box,
    "camera": Camera,
    "circle": Circle,
    "cone": Cone,
    "cylinder": Cylinder,
    "dodecahedron": Dodecahedron,
    "gltf-model": GLTF,
    "icosahedron": Icosahedron,
    "image": Image,
    "landmarks": Landmarks,
    "light": Light,
    "line": Line,
    "object": Object,
    "entity": Object,
    "octahedron": Octahedron,
    "particle": Particle,
    "plane": Plane,
    "ring": Ring,
    "sphere": Sphere,
    "tetrahedron": Tetrahedron,
    "text": Text,
    "thickline": ThickLine,
    "torus": Torus,
    "torusKnot": TorusKnot,
    "triangle": Triangle,
}
