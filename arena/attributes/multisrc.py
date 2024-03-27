from .attribute import Attribute


class Multisrc(Attribute):
    """
    Multisrc attribute class to manage its properties in the ARENA: Define multiple visual sources applied to an object.
    Usage: `multisrc=Multisrc(...)`

    :param str srcs: A comma-delimited list if URIs, e.g. 'side1.png, side2.png, side3.png, side4.png, side5.png, side6.png' (required). (optional)
    :param str srcspath: URI, relative or full path of a directory containing srcs, e.g. 'store/users/wiselab/images/dice/' (required). (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
