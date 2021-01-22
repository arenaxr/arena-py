from ..utils import Utils
from .attribute import Attribute

class Sound(Attribute):
    """
    Sound Attribute.
    Usage: sound=Sound(...)
    """
    def __init__(self, src, positional=False, **kwargs):
        super().__init__(src=src, positional=positional, **kwargs)
