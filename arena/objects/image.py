from .arena_object import Object

class Image(Object):
    """
    Class for Image in the ARENA: Display an image on a plane.  See guidance to store paths under (https://docs.arenaxr.org/content/interface/filestore.html) ARENA File Store, CDN, or DropBox.
    
    :param str url: Store File Store file paths under 'store/users/<username>', see CDN and other storage options in the description above. (optional)
    :param float height: height, defaults to '1' (optional)
    :param int segmentsHeight: segments height, defaults to '1' (optional)
    :param int segmentsWidth: segments width, defaults to '1' (optional)
    :param float width: width, defaults to '1' (optional)
    """
    object_type = "image"

    def __init__(self, url="", **kwargs):
        super().__init__(object_type=Image.object_type, url=url, **kwargs)
