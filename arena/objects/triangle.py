from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Triangle:
    """
    Triangle
    Triangle Geometry.

    :param str object_type: 3D object type.. Must be 'triangle'.
    :param dict vertexA: Vector3. Defaults to {'x': 0, 'y': 0.5, 'z': 0}
    :param dict vertexB: Vector3. Defaults to {'x': -0.5, 'y': -0.5, 'z': 0}
    :param dict vertexC: Vector3. Defaults to {'x': 0.5, 'y': -0.5, 'z': 0}
    """
    object_type: str
    vertexA: dict = field(default_factory=lambda: {'x': 0, 'y': 0.5, 'z': 0})
    vertexB: dict = field(default_factory=lambda: {'x': -0.5, 'y': -0.5, 'z': 0})
    vertexC: dict = field(default_factory=lambda: {'x': 0.5, 'y': -0.5, 'z': 0})
