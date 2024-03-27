from .attribute import Attribute


class ModelUpdate(Attribute):
    """
    ModelUpdate attribute class to manage its properties in the ARENA: The GLTF-specific `modelUpdate` attribute is an object with child component names as keys. The top-level keys are the names of the child components to be updated. The values of each are nested `position` and `rotation` attributes to set as new values, respectively. Either `position` or `rotation` can be omitted if unchanged.
    Usage: `modelUpdate=ModelUpdate(...)`

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
