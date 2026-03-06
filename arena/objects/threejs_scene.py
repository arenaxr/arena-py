from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ThreejsScene:
    """
    Three.js Scene
    Load a Three.js Scene. Could be THREE.js version-specific; you can see the THREE.js version in the JS console once you open ARENA; using glTF is preferred. Format: <a href='https://threejs.org/docs/#api/en/scenes/Scene'>THREE.js Scene</a>. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'threejs-scene'.
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    """
    object_type: str
    url: str
