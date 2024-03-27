from .attribute import Attribute


class GltfMorph(Attribute):
    """
    GltfMorph attribute class to manage its properties in the ARENA: Allows you to target and control a gltf model's morphTargets created in Blender. More properties at <https://github.com/elbobo/aframe-gltf-morph-component> A-Frame GLTF Morph component.
    Usage: `gltf_morph=GltfMorph(...)`

    :param str morphtarget: Name of morphTarget, can be found as part of the GLTF model. (optional)
    :param float value: Value that you want to set that morphTarget to (0 - 1). (optional)
    """

    def __init__(self, morphtarget, value):
        self.morphtarget = str(morphtarget)
        self.value = str(value)


class Morph(GltfMorph):
    """
    Alternate name for GltfMorph.
    Usage: `gltf_morph=Morph(...)`
    """
