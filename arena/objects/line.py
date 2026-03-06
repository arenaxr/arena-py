from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Line:
    """
    Line
    Draw a line.

    :param str object_type: 3D object type.. Must be 'line'.
    :param str color: Line color.. Defaults to '#74BEC1'
    :param dict end: End coordinate.. Defaults to {'x': -0.5, 'y': -0.5, 'z': 0}
    :param float opacity: Line opacity., optional. Defaults to 1
    :param dict start: Start point coordinate.. Defaults to {'x': 0, 'y': 0.5, 'z': 0}
    :param bool visible: Whether object is visible. Property is inherited., optional. Defaults to True
    """
    object_type: str
    color: str = '#74BEC1'
    end: dict = field(default_factory=lambda: {'x': -0.5, 'y': -0.5, 'z': 0})
    opacity: Optional[float] = 1
    start: dict = field(default_factory=lambda: {'x': 0, 'y': 0.5, 'z': 0})
    visible: Optional[bool] = True
