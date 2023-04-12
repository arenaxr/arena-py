from .arena_object import Object
from .box import Box
from .camera import Camera
from .circle import Circle
from .cone import Cone
from .cylinder import Cylinder
from .dodecahedron import Dodecahedron
from .entity import Entity
from .gltf import GLTF
from .icosahedron import Icosahedron
from .image import Image
from .light import Light
from .line import Line
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
    "camera": Camera,
    "circle": Circle,
    "cone": Cone,
    "cube": Box,
    "cylinder": Cylinder,
    "dodecahedron": Dodecahedron,
    "entity": Entity,
    "gltf-model": GLTF,
    "icosahedron": Icosahedron,
    "image": Image,
    "light": Light,
    "line": Line,
    "object": Object,
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
