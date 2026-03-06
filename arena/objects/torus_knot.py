from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class TorusKnot:
    """
    Torus Knot
    Torus Knot Geometry.

    :param str object_type: 3D object type.. Must be 'torusKnot'.
    :param float p: P, optional. Defaults to 2
    :param float q: Q, optional. Defaults to 3
    :param float radius: radius. Defaults to 1
    :param float radiusTubular: radius tubular. Defaults to 0.2
    :param int segmentsRadial: segments radial, optional. Defaults to 8
    :param int segmentsTubular: segments tubular, optional. Defaults to 100
    """
    object_type: str
    p: Optional[float] = 2
    q: Optional[float] = 3
    radius: float = 1
    radiusTubular: float = 0.2
    segmentsRadial: Optional[int] = 8
    segmentsTubular: Optional[int] = 100
