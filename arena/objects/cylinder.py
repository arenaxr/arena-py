from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Cylinder:
    """
    Cylinder
    Cylinder Geometry.

    :param str object_type: 3D object type.. Must be 'cylinder'.
    :param float height: height. Defaults to 1
    :param bool openEnded: open ended, optional. Defaults to False
    :param float radius: radius. Defaults to 1
    :param int segmentsHeight: segments height, optional. Defaults to 18
    :param int segmentsRadial: segments radial, optional. Defaults to 36
    :param float thetaLength: theta length, optional. Defaults to 360
    :param float thetaStart: theta start, optional. Defaults to 0
    """
    object_type: str
    height: float = 1
    openEnded: Optional[bool] = False
    radius: float = 1
    segmentsHeight: Optional[int] = 18
    segmentsRadial: Optional[int] = 36
    thetaLength: Optional[float] = 360
    thetaStart: Optional[float] = 0
