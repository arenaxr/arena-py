from .arena_object import Object

class Image(Object):
    """
    Class for Image in the ARENA.
    """
    object_type = "image"

    def __init__(self, url="", **kwargs):
        super().__init__(object_type=Image.object_type, url=url, **kwargs)
