from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Tetrahedron:
    """
    Tetrahedron
    Tetrahedron Geometry.

    :param str object_type: 3D object type.. Must be 'tetrahedron'.
    :param int detail: detail, optional. Defaults to 0
    :param float radius: radius. Defaults to 1
    """
    object_type: str
    detail: Optional[int] = 0
    radius: float = 1
