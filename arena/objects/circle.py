from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Circle:
    """
    Circle
    Circle Geometry.

    :param str object_type: 3D object type.. Must be 'circle'.
    :param float radius: radius. Defaults to 1
    :param int segments: segments, optional. Defaults to 32
    :param float thetaLength: theta length, optional. Defaults to 360
    :param float thetaStart: theta start, optional. Defaults to 0
    """
    object_type: str
    radius: float = 1
    segments: Optional[int] = 32
    thetaLength: Optional[float] = 360
    thetaStart: Optional[float] = 0
