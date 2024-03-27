from .attribute import Attribute


class MaterialExtras(Attribute):
    """
    MaterialExtras attribute class to manage its properties in the ARENA: Define extra material properties, namely texture encoding, whether to render the material's color and render order. The properties set here access directly Three.js material component.  More properties at <https://threejs.org/docs/#api/en/materials/Material> THREE.js Material.
    Usage: `material_extras=MaterialExtras(...)`

    :param str colorSpace: The material colorspace. Allows [SRGBColorSpace, LinearSRGBColorSpace, DisplayP3ColorSpace, NoColorSpace] Defaults to 'SRGBColorSpace' (optional)
    :param bool colorWrite: Whether to render the material's color. Defaults to 'True' (optional)
    :param float gltfOpacity: Opacity value to apply to the model. 1 is fully opaque, 0 is fully transparent. Defaults to '1' (optional)
    :param str overrideSrc: Overrides the material source in all meshes of an object (e.g. a basic shape or a GLTF); Use, for example, to change the texture of a GLTF. (optional)
    :param float renderOrder: Allows the default rendering order of scene graph objects to be overridden. Defaults to '1' (optional)
    :param bool transparentOccluder: If `true`, will set `colorWrite=false` and `renderOrder=0` to make the material a transparent occluder. (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
