from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Image:
    """
    Image
    Display an image on a plane. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'image'.
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    :param float height: height. Defaults to 1
    :param int segmentsHeight: segments height, optional. Defaults to 1
    :param int segmentsWidth: segments width, optional. Defaults to 1
    :param float width: width. Defaults to 1
    """
    object_type: str
    url: str
    height: float = 1
    segmentsHeight: Optional[int] = 1
    segmentsWidth: Optional[int] = 1
    width: float = 1
