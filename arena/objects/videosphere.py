from .arena_object import Object

class Videosphere(Object):
    """
    Class for Videosphere in the ARENA: Videosphere Geometry
    
    :param bool autoplay: autoplay; defaults to 'True' (optional)
    :param str crossOrigin: crossOrigin; defaults to 'anonymous' (optional)
    :param bool loop: loop; defaults to 'True' (optional)
    :param float radius: radius; defaults to '5000' (optional)
    :param int segmentsHeight: segments height; defaults to '64' (optional)
    :param int segmentsWidth: segments width; defaults to '64' (optional)
    :param str src: URI, relative or full path of an image/video file. e.g. 'store/users/wiselab/images/360falls.mp4' (optional)
    """
    object_type = "videosphere"

    def __init__(self, **kwargs):
        super().__init__(object_type=Videosphere.object_type, **kwargs)
