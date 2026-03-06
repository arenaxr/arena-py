from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Torus:
    """
    Torus
    Torus Geometry.

    :param str object_type: 3D object type.. Must be 'torus'.
    :param float arc: Arc, optional. Defaults to 360
    :param float radius: radius. Defaults to 1
    :param float radiusTubular: radius tubular. Defaults to 0.2
    :param int segmentsRadial: segments radial, optional. Defaults to 36
    :param int segmentsTubular: segments tubular, optional. Defaults to 32
    """
    object_type: str
    arc: Optional[float] = 360
    radius: float = 1
    radiusTubular: float = 0.2
    segmentsRadial: Optional[int] = 36
    segmentsTubular: Optional[int] = 32
