from .attribute import Attribute

class JitsiVideo(Attribute):
    """
    Jitsi Video Attribute. For video source.
    Usage: jitsi_video=JitsiVideo(...)
    """
    def __init__(self, jitsiId=None, displayName=None):
        # Since jitsiId overrides displayName, do not set None arguments
        kwargs = {}
        if jitsiId is not None:
            kwargs['jitsiId'] = jitsiId
        if displayName is not None:
            kwargs['displayName'] = displayName
        super().__init__(**kwargs)
