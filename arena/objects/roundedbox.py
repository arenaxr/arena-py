from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Roundedbox:
    """
    Rounded Box
    Rounded Box Geometry.

    :param str object_type: 3D object type.. Must be 'roundedbox'.
    :param float depth: depth. Defaults to 1
    :param float height: height. Defaults to 1
    :param float width: width. Defaults to 1
    :param float radius: radius of edge. Defaults to 0.15
    :param int radiusSegments: segments radius, optional. Defaults to 10
    """
    object_type: str
    depth: float = 1
    height: float = 1
    width: float = 1
    radius: float = 0.15
    radiusSegments: Optional[int] = 10
