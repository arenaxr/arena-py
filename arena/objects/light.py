from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Light:
    """
    Light
    A light. More properties at <a href='https://aframe.io/docs/1.5.0/components/light.html'>A-Frame Light</a>.

    :param str object_type: 3D object type.. Must be 'light'.
    :param float angle: Maximum extent of spot light from its direction (in degrees). Requires `type: spot`., optional. Defaults to 60
    :param bool castShadow: Whether this light casts shadows on the scene., optional. Defaults to False
    :param str color: Light color. For 'hemisphere', light color from above.. Defaults to '#ffffff'
    :param float decay: Amount the light dims along the distance of the light. Requires `type: point` or `spot`., optional. Defaults to 1
    :param float distance: Distance where intensity becomes 0. If distance is 0, then the point light does not decay with distance. Requires `type: point` or `spot`., optional. Defaults to 0
    :param str envMap: Cube Map to load., optional.
    :param str groundColor: Light color from below. Requires `type: hemisphere`., optional. Defaults to '#ffffff'
    :param float intensity: Amount of light provided.. Defaults to 1
    :param dict light: DEPRECATED: data.light.[property] is deprecated, use object_type: light and data.[property] instead., optional.
    :param float penumbra: Percent of the spotlight cone that is attenuated due to penumbra. Requires `type: spot`., optional. Defaults to 0
    :param float shadowBias: Offset depth when deciding whether a surface is in shadow. Tiny adjustments here (in the order of +/-0.0001) may reduce artifacts in shadows., optional. Defaults to 0
    :param float shadowCameraBottom: Bottom plane of shadow camera frustum. Requires `type: directional`., optional. Defaults to -5
    :param float shadowCameraFar: Far plane of shadow camera frustum., optional. Defaults to 500
    :param float shadowCameraFov: Shadow camera's FOV. Requires `type: point` or `spot`., optional. Defaults to 50
    :param float shadowCameraLeft: Left plane of shadow camera frustum. Requires `type: directional`., optional. Defaults to -5
    :param float shadowCameraNear: Near plane of shadow camera frustum., optional. Defaults to 0.5
    :param float shadowCameraRight: Right plane of shadow camera frustum. Requires `type: directional`., optional. Defaults to 5
    :param float shadowCameraTop: Top plane of shadow camera frustum. Requires `type: directional`., optional. Defaults to 5
    :param bool shadowCameraVisible: Displays a visual aid showing the shadow camera's position and frustum. This is the light's view of the scene, used to project shadows., optional. Defaults to False
    :param float shadowMapHeight: Shadow map's vertical resolution. Larger shadow maps display more crisp shadows, at the cost of performance., optional. Defaults to 512
    :param float shadowMapWidth: Shadow map's horizontal resolution., optional. Defaults to 512
    :param float shadowRadius: shadowRadius, optional. Defaults to 1
    :param str target: Id of element the spot should point to. Set to null to transform spotlight by orientation, pointing to it's -Z axis. Requires `type: spot`., optional.
    :param str type: The type of light, or what shape the light should take.. Allows ['ambient', 'directional', 'hemisphere', 'point', 'spot']. Defaults to 'directional'
    """
    object_type: str
    angle: Optional[float] = 60
    castShadow: Optional[bool] = False
    color: str = '#ffffff'
    decay: Optional[float] = 1
    distance: Optional[float] = 0
    envMap: Optional[str] = None
    groundColor: Optional[str] = '#ffffff'
    intensity: float = 1
    light: Optional[dict] = None
    penumbra: Optional[float] = 0
    shadowBias: Optional[float] = 0
    shadowCameraBottom: Optional[float] = -5
    shadowCameraFar: Optional[float] = 500
    shadowCameraFov: Optional[float] = 50
    shadowCameraLeft: Optional[float] = -5
    shadowCameraNear: Optional[float] = 0.5
    shadowCameraRight: Optional[float] = 5
    shadowCameraTop: Optional[float] = 5
    shadowCameraVisible: Optional[bool] = False
    shadowMapHeight: Optional[float] = 512
    shadowMapWidth: Optional[float] = 512
    shadowRadius: Optional[float] = 1
    target: Optional[str] = None
    type: str = 'directional'
