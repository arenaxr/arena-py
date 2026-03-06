from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Sphere:
    """
    Sphere
    Sphere Geometry.

    :param str object_type: 3D object type.. Must be 'sphere'.
    :param float phiLength: phi length, optional. Defaults to 360
    :param float phiStart: phi start, optional. Defaults to 0
    :param float radius: radius. Defaults to 1
    :param int segmentsHeight: segments height, optional. Defaults to 18
    :param int segmentsWidth: segments width, optional. Defaults to 36
    :param float thetaLength: theta length, optional. Defaults to 180
    :param float thetaStart: theta start, optional. Defaults to 0
    """
    object_type: str
    phiLength: Optional[float] = 360
    phiStart: Optional[float] = 0
    radius: float = 1
    segmentsHeight: Optional[int] = 18
    segmentsWidth: Optional[int] = 36
    thetaLength: Optional[float] = 180
    thetaStart: Optional[float] = 0
