from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Thickline:
    """
    Thickline
    Draw a line that can have a custom width.

    :param str object_type: 3D object type.. Must be 'thickline'.
    :param str color: Line color.. Defaults to '#000000'
    :param float lineWidth: Width of line in px.. Defaults to 1
    :param str lineWidthStyler: Allows defining the line width as a function of relative position p along the path of the line. By default it is set to a constant 1. You may also choose one of the preset functions.. Allows ['default', 'grow', 'shrink', 'center-sharp', 'center-smooth', 'sine-wave']. Defaults to 'default'
    :param str path: Comma-separated list of x y z coordinates of the line vertices.. Defaults to '-2 -1 0, 0 20 0, 10 -1 10'
    """
    object_type: str
    color: str = '#000000'
    lineWidth: float = 1
    lineWidthStyler: str = 'default'
    path: str = '-2 -1 0, 0 20 0, 10 -1 10'
