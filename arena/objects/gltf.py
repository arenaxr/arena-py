from .arena_object import Object

class GLTF(Object):
    """
    Class for GLTF Model in the ARENA.
    """
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="gltf-model", url=url, **kwargs)
