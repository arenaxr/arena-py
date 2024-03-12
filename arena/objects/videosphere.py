from .arena_object import Object

class Videosphere(Object):
    """
    Videosphere object class to manage its properties in the ARENA: Videosphere Geometry.

    :param bool autoplay: Autoplay Defaults to 'True' (optional)
    :param str crossOrigin: Cross Origin Defaults to 'anonymous' (optional)
    :param bool loop: Loop Defaults to 'True' (optional)
    :param float radius: Radius Defaults to '500' (optional)
    :param int segmentsHeight: Segments Height Defaults to '32' (optional)
    :param int segmentsWidth: Segments Width Defaults to '64' (optional)
    :param str src: URI, relative or full path of an image/video file. e.g. 'store/users/wiselab/images/360falls.mp4'. (optional)
    """
    object_type = "videosphere"

    def __init__(self, **kwargs):
        super().__init__(object_type=Videosphere.object_type, **kwargs)
