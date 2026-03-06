from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Capsule:
    """
    Capsule
    Capsule Geometry.

    :param str object_type: 3D object type.. Must be 'capsule'.
    :param float length: length. Defaults to 1
    :param float radius: radius. Defaults to 1
    :param int segmentsCap: segments capsule, optional. Defaults to 18
    :param int segmentsRadial: segments radial, optional. Defaults to 36
    """
    object_type: str
    length: float = 1
    radius: float = 1
    segmentsCap: Optional[int] = 18
    segmentsRadial: Optional[int] = 36
