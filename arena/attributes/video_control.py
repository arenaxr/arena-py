from .attribute import Attribute

class VideoControl(Attribute):
    """
    VideoControl attribute class to manage its properties in the ARENA: Video Control
    Usage: video_control=VideoControl(...)
    
    :param str frame_object: URL of a thumbnail image, e.g. 'store/users/wiselab/images/conix-face-white.jpg' (optional)
    :param str video_object: Name of object where to put the video, e.g. 'square_vid6' (optional)
    :param str video_path: URL of the video file, e.g. 'store/users/wiselab/videos/kungfu.mp4' (optional)
    :param bool anyone_clicks: Responds to clicks from any user; defaults to 'True' (optional)
    :param bool video_loop: Video automatically loops; defaults to 'True' (optional)
    :param bool autoplay: Video starts playing automatically (optional)
    :param float volume: Video sound volume; defaults to '1' (optional)
    :param bool cleanup: Automatically remove HTML5 video and img assets from DOM on object removal; defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
