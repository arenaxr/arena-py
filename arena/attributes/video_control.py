from .attribute import Attribute

class VideoControl(Attribute):
    """
    VideoControl attribute class to manage its properties in the ARENA: Adds a video to an entity and controls its playback.
    Usage: `video_control=VideoControl(...)`

    :param bool anyone_clicks: Responds to clicks from any user. Defaults to 'True' (optional)
    :param bool autoplay: Video starts playing automatically. (optional)
    :param bool cleanup: Automatically remove HTML5 video and img assets from DOM on object removal. Defaults to 'True' (optional)
    :param str frame_object: URL of a thumbnail image, e.g. 'store/users/wiselab/images/conix-face-white.jpg'. (optional)
    :param bool video_loop: Video automatically loops. Defaults to 'True' (optional)
    :param str video_object: Name of object where to put the video, e.g. 'square_vid6'. (optional)
    :param str video_path: URL of the video file, e.g. 'store/users/wiselab/videos/kungfu.mp4'. (optional)
    :param float volume: Video sound volume. Defaults to '1' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
