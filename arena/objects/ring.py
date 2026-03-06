from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Ring:
    """
    Ring
    Ring Geometry.

    :param str object_type: 3D object type.. Must be 'ring'.
    :param float radiusInner: radius inner. Defaults to 0.8
    :param float radiusOuter: radius outer. Defaults to 1.2
    :param int segmentsPhi: segments phi, optional. Defaults to 10
    :param int segmentsTheta: segments theta, optional. Defaults to 32
    :param float thetaLength: theta length, optional. Defaults to 360
    :param float thetaStart: theta start, optional. Defaults to 0
    """
    object_type: str
    radiusInner: float = 0.8
    radiusOuter: float = 1.2
    segmentsPhi: Optional[int] = 10
    segmentsTheta: Optional[int] = 32
    thetaLength: Optional[float] = 360
    thetaStart: Optional[float] = 0
