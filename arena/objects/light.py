from .arena_object import Object

class Light(Object):
    """
    Light object class to manage its properties in the ARENA: A light. More properties at <https://aframe.io/docs/1.5.0/components/light.html> A-Frame Light.

    :param float angle: Maximum extent of spot light from its direction (in degrees). Requires type:spot. Defaults to '60' (optional)
    :param bool castShadow: Whether this light casts shadows on the scene. (optional)
    :param str color: Light color. For 'hemisphere', light color from above. Defaults to '#ffffff' (optional)
    :param float decay: Amount the light dims along the distance of the light. Requires type:point or type:spot. Defaults to '1' (optional)
    :param float distance: Distance where intensity becomes 0. If distance is 0, then the point light does not decay with distance. Requires type:point or type:spot. (optional)
    :param str envMap: Cube Map to load. (optional)
    :param str groundColor: Light color from below. Requires type:hemisphere. Defaults to '#ffffff' (optional)
    :param float intensity: Amount of light provided. Defaults to '1' (optional)
    :param dict light: light (optional)
    :param float penumbra: Percent of the spotlight cone that is attenuated due to penumbra. Requires type:spot. (optional)
    :param float shadowBias: Offset depth when deciding whether a surface is in shadow. Tiny adjustments here (in the order of +/-0.0001) may reduce artifacts in shadows. (optional)
    :param float shadowCameraBottom: Bottom plane of shadow camera frustum. Requires type:directional. Defaults to '-5' (optional)
    :param float shadowCameraFar: Far plane of shadow camera frustum. Defaults to '500' (optional)
    :param float shadowCameraFov: Shadow camera's FOV. Requires type:point or spot. Defaults to '50' (optional)
    :param float shadowCameraLeft: Left plane of shadow camera frustum. Requires type:directional. Defaults to '-5' (optional)
    :param float shadowCameraNear: Near plane of shadow camera frustum. Defaults to '0.5' (optional)
    :param float shadowCameraRight: Right plane of shadow camera frustum. Requires type:directional. Defaults to '5' (optional)
    :param float shadowCameraTop: Top plane of shadow camera frustum. Requires type:directional. Defaults to '5' (optional)
    :param bool shadowCameraVisible: Displays a visual aid showing the shadow camera's position and frustum. This is the light's view of the scene, used to project shadows. (optional)
    :param float shadowMapHeight: Shadow map's vertical resolution. Larger shadow maps display more crisp shadows, at the cost of performance. Defaults to '512' (optional)
    :param float shadowMapWidth: Shadow map's horizontal resolution. Defaults to '512' (optional)
    :param float shadowRadius: shadowRadius (castShadow=true) Defaults to '1' (optional)
    :param str target: Id of element the spot should point to. Set to null to transform spotlight by orientation, pointing to it's -Z axis. Requires type:spot. (optional)
    :param str type: The type of light, or what shape the light should take. Allows [ambient, directional, hemisphere, point, spot] Defaults to 'directional' (optional)
    """
    object_type = "light"

    def __init__(self, **kwargs):
        super().__init__(object_type=Light.object_type, **kwargs)
