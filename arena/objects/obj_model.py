from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ObjModel:
    """
    OBJ Model
    Loads a 3D model and material using a Wavefront (.OBJ) file and a .MTL file. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'obj-model'.
    :param str obj: Url pointing to a .OBJ file. Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    :param str mtl: Url pointing to a .MTL file. Optional if you wish to use the material component instead., optional.
    """
    object_type: str
    obj: str
    mtl: Optional[str] = None
