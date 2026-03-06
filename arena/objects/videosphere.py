from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Videosphere:
    """
    Videosphere
    Videosphere Geometry.

    :param str object_type: 3D object type.. Must be 'videosphere'.
    :param bool autoplay: Autoplay, optional. Defaults to True
    :param str crossOrigin: Cross Origin, optional. Defaults to 'anonymous'
    :param bool loop: Loop, optional. Defaults to True
    :param float radius: Radius. Defaults to 500
    :param int segmentsHeight: Segments Height, optional. Defaults to 32
    :param int segmentsWidth: Segments Width, optional. Defaults to 64
    :param str src: URI, relative or full path of an image/video file. e.g. 'store/users/wiselab/images/360falls.mp4'., optional.
    """
    object_type: str
    autoplay: Optional[bool] = True
    crossOrigin: Optional[str] = 'anonymous'
    loop: Optional[bool] = True
    radius: float = 500
    segmentsHeight: Optional[int] = 32
    segmentsWidth: Optional[int] = 64
    src: Optional[str] = None
