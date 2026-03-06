from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Box:
    """
    Box
    Box Geometry.

    :param str object_type: 3D object type.. Must be 'box'.
    :param float depth: depth. Defaults to 1
    :param float height: height. Defaults to 1
    :param int segmentsDepth: segments depth, optional. Defaults to 1
    :param int segmentsHeight: segments height, optional. Defaults to 1
    :param int segmentsWidth: segments width, optional. Defaults to 1
    :param float width: width. Defaults to 1
    """
    object_type: str
    depth: float = 1
    height: float = 1
    segmentsDepth: Optional[int] = 1
    segmentsHeight: Optional[int] = 1
    segmentsWidth: Optional[int] = 1
    width: float = 1
