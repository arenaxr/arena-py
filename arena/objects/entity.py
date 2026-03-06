from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Entity:
    """
    Entity (generic object)
    Entities are the base of all objects in the scene. Entities are containers into which components can be attached.

    :param str object_type: 3D object type.. Must be 'entity'.
    :param dict geometry: The primitive mesh geometry., optional.
    :param dict panel: The rounded UI panel primitive., optional.
    """
    object_type: str
    geometry: Optional[dict] = None
    panel: Optional[dict] = None
