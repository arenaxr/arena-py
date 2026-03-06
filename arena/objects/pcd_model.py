from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class PcdModel:
    """
    PCD Model
    Load a PCD model. Format: <a href='https://pointclouds.org/documentation/tutorials/index.html'>Point Clouds</a>. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'pcd-model'.
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    :param float pointSize: Size of the points.. Defaults to 0.01
    :param str pointColor: Color of the points., optional. Defaults to ''
    :param float opacity: Opacity of all points.. Defaults to 1
    """
    object_type: str
    url: str
    pointSize: float = 0.01
    pointColor: Optional[str] = ''
    opacity: float = 1
