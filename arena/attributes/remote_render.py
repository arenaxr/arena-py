from .attribute import Attribute


class RemoteRender(Attribute):
    """
    RemoteRender attribute class to manage its properties in the ARENA: Whether or not an object should be remote rendered [Experimental].
    Usage: `remote_render=RemoteRender(...)`

    :param bool enabled: Remote Render this object. Defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
