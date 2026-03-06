from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class HandRight:
    """
    Hand
    Hand is the (left or right) hand metadata pose and controller type of the user avatar.

    :param str object_type: 3D object type.. Allows ['handLeft', 'handRight'].
    :param str url: Path to user avatar hand model.. Defaults to 'static/models/hands/valve_index_left.gltf'
    :param str dep: Camera object_id this hand belongs to.. Defaults to ''
    """
    object_type: str
    url: str = 'static/models/hands/valve_index_left.gltf'
    dep: str = ''
