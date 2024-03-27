from ..utils import Utils
from .attribute import Attribute
from .position import Position

class Landmark(Attribute):
    """
    Landmark attribute class to manage its properties in the ARENA: Define entities as a landmark; Landmarks appears in the landmark list and you can move (teleport) to them; You can define the behavior of the teleport: if you will be at a fixed or random distance, looking at the landmark, fixed offset or if it is constrained by a navmesh (when it exists).
    Usage: `landmark=Landmark(...)`

    :param str constrainToNavMesh: Teleports should snap to navmesh. Allows [false, any, coplanar] Defaults to 'false' (optional)
    :param str label: Landmark description to display in the landmark list. (optional)
    :param bool lookAtLandmark: Set to true to make users face the landmark when teleported to it. Defaults to 'True' (optional)
    :param dict offsetPosition: Use as a static teleport x,y,z offset. Defaults to '{'x': 0, 'y': 1.6, 'z': 0}' (optional)
    :param float randomRadiusMax: Maximum radius from the landmark to teleport to. (optional)
    :param float randomRadiusMin: Minimum radius from the landmark to teleport to. (randomRadiusMax must > 0). (optional)
    :param bool startingPosition: Set to true to use this landmark as a scene start (spawn) position. If several landmarks with startingPosition=true exist in a scene, one will be randomly selected. (optional)
    """
    def __init__(self, **kwargs):
        if "offsetPosition" in kwargs:
            if isinstance(kwargs["offsetPosition"], tuple) or isinstance(kwargs["offsetPosition"], list):
                kwargs["offsetPosition"] = Utils.tuple_to_string(kwargs["offsetPosition"])
            # can get away with using Position.to_str() even if animation is rotation (euler) or scale
            # since we just want the 3 values to be a space separated string
            elif isinstance(kwargs["offsetPosition"], Position):
                kwargs["offsetPosition"] = kwargs["offsetPosition"].to_str()
        super().__init__(**kwargs)
