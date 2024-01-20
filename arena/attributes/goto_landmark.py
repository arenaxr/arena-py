from .attribute import Attribute


class GotoLandmark(Attribute):
    """
    GotoLandmark attribute class to manage its properties in the ARENA: Teleports user to the landmark with the given name; Requires click-listener
    Usage: goto_landmark=GotoLandmark(...)
    
    :param str landmark: Id of landmark to teleport to. (optional)
    :param str on: Event to listen 'on'. [mousedown, mouseup]; defaults to 'mousedown' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
