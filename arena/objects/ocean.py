from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Ocean:
    """
    Ocean
    Flat-shaded ocean primitive.

    :param str object_type: 3D object type.. Must be 'ocean'.
    :param float width: Width of the ocean area.. Defaults to 10
    :param float depth: Depth of the ocean area.. Defaults to 10
    :param float density: Density of waves., optional. Defaults to 10
    :param float amplitude: Wave amplitude., optional. Defaults to 0.1
    :param float amplitudeVariance: Wave amplitude variance., optional. Defaults to 0.3
    :param float speed: Wave speed., optional. Defaults to 1
    :param float speedVariance: Wave speed variance., optional. Defaults to 2
    :param str color: Wave color.. Defaults to '#7AD2F7'
    :param float opacity: Wave opacity., optional. Defaults to 0.8
    """
    object_type: str
    width: float = 10
    depth: float = 10
    density: Optional[float] = 10
    amplitude: Optional[float] = 0.1
    amplitudeVariance: Optional[float] = 0.3
    speed: Optional[float] = 1
    speedVariance: Optional[float] = 2
    color: str = '#7AD2F7'
    opacity: Optional[float] = 0.8
