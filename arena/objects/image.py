from .arena_object import Object

class Image(Object):
    """
    Class for Image in the ARENA.
    """
    def __init__(self, url="", **kwargs):
        super().__init__(object_type="image", url=url, **kwargs)
