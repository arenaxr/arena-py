from .attribute import Attribute

class VideoControl(Attribute):
    """
    VideoControl Attribute.
    Usage: video_control=VideoControl(...)
    """
    def __init__(self, video_object, video_path, anyone_clicks=True, video_loop=True, autoplay=True, volume=1.0):
        super().__init__(video_object=video_object, video_path=video_path, 
                         anyone_clicks=anyone_clicks, video_loop=video_loop, autoplay=autoplay, volume=volume)