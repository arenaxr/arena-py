from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class UrdfModel:
    """
    URDF Model
    Load a URDF model. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'urdf-model'.
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    :param str urlBase: Base path for xacro/urdf package includes. This must be an absolute path with no trailing slash, e.g. '/store/users/username/robot'.
    :param str joints: Set joint values (in degrees) in the form 'JointName1: ValueInDegrees1, JointName2: ValueInDegrees2, ...'., optional.
    """
    object_type: str
    url: str
    urlBase: str
    joints: Optional[str] = None
