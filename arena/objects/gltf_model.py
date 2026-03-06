from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class GltfModel:
    """
    GLTF Model
    Load a GLTF model. Besides applying standard rotation and position attributes to the center-point of the GLTF model, the individual child components can also be manually manipulated. See format details in the `modelUpdate` data attribute. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'gltf-model'.
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    """
    object_type: str
    url: str
