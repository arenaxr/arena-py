from .attribute import Attribute


class GltfModelLod(Attribute):
    """
    GltfModelLod attribute class to manage its properties in the ARENA: Simple switch between the default gltf-model and a detailed one when a user camera is within specified distance
    Usage: gltf_model_lod=GltfModelLod(...)
    
    :param str detailedUrl: Alternative 'detailed' gltf model to load by URL (optional)
    :param float detailedDistance: At what distance to switch between the models; defaults to '10' (optional)
    :param float updateRate: How often user camera is checked for LOD (default 333ms); defaults to '333' (optional)
    :param bool retainCache: Whether to skip freeing the detailed model from browser cache (default false) (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
