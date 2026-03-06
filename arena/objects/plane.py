from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Plane:
    """
    Plane
    Plane Geometry.

    :param str object_type: 3D object type.. Must be 'plane'.
    :param float height: height. Defaults to 1
    :param int segmentsHeight: segments height, optional. Defaults to 1
    :param int segmentsWidth: segments width, optional. Defaults to 1
    :param float width: width. Defaults to 1
    """
    object_type: str
    height: float = 1
    segmentsHeight: Optional[int] = 1
    segmentsWidth: Optional[int] = 1
    width: float = 1
