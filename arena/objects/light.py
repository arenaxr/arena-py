from .arena_object import Object

class Light(Object):
    """
    Class for Light in the ARENA: A light.  More properties at (https://aframe.io/docs/1.5.0/components/light.html) A-Frame Light.
    
    :param float angle: Maximum extent of spot light from its direction (in degrees). NOTE: Spot light type only., defaults to '60' (optional)
    :param bool castShadow: castShadow (point, spot, directional) (optional)
    :param str color: Light color., defaults to '#ffffff' (optional)
    :param float decay: Amount the light dims along the distance of the light. NOTE: Point and Spot light type only., defaults to '1' (optional)
    :param float distance: Distance where intensity becomes 0. If distance is 0, then the point light does not decay with distance. NOTE: Point and Spot light type only. (optional)
    :param str groundColor: Light color from below. NOTE: Hemisphere light type only, defaults to '#ffffff' (optional)
    :param float intensity: Light strength., defaults to '1' (optional)
    :param dict light:  (optional)
    :param float penumbra: Percent of the spotlight cone that is attenuated due to penumbra. NOTE: Spot light type only. (optional)
    :param float shadowBias: shadowBias (castShadow=true) (optional)
    :param float shadowCameraBottom: shadowCameraBottom (castShadow=true), defaults to '-5' (optional)
    :param float shadowCameraFar: shadowCameraFar (castShadow=true), defaults to '500' (optional)
    :param float shadowCameraFov: shadowCameraFov (castShadow=true), defaults to '90' (optional)
    :param float shadowCameraLeft: shadowCameraBottom (castShadow=true), defaults to '-5' (optional)
    :param float shadowCameraNear: shadowCameraNear (castShadow=true), defaults to '0.5' (optional)
    :param float shadowCameraRight: shadowCameraRight (castShadow=true), defaults to '5' (optional)
    :param float shadowCameraTop: shadowCameraTop (castShadow=true), defaults to '5' (optional)
    :param bool shadowCameraVisible: shadowCameraVisible (castShadow=true) (optional)
    :param float shadowMapHeight: shadowMapHeight (castShadow=true), defaults to '512' (optional)
    :param float shadowMapWidth: shadowMapWidth (castShadow=true), defaults to '512' (optional)
    :param float shadowRadius: shadowRadius (castShadow=true), defaults to '1' (optional)
    :param str target: Id of element the spot should point to. set to null to transform spotlight by orientation, pointing to it’s -Z axis. NOTE: Spot light type only. (optional)
    :param str type: The type of light, or what shape the light should take. [ambient, directional, hemisphere, point, spot], defaults to 'directional' (optional)
    """
    object_type = "light"

    def __init__(self, **kwargs):
        super().__init__(object_type=Light.object_type, **kwargs)
