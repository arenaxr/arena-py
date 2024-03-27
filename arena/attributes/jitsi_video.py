from .attribute import Attribute

class JitsiVideo(Attribute):
    """
    JitsiVideo attribute class to manage its properties in the ARENA: Apply a jitsi video source to the geometry.
    Usage: `jitsi_video=JitsiVideo(...)`

    :param str displayName: ARENA or Jitsi display name of the video source; Will be ignored if jitsiId is given. (* change requires reload* ). (optional)
    :param str jitsiId: JitsiId of the video source; If defined will override displayName. (optional)
    """
    def __init__(self, jitsiId=None, displayName=None):
        # Since jitsiId overrides displayName, do not set None arguments
        kwargs = {}
        if jitsiId is not None:
            kwargs['jitsiId'] = jitsiId
        if displayName is not None:
            kwargs['displayName'] = displayName
        super().__init__(**kwargs)
