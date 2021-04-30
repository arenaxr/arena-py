from ..utils import Utils
from .attribute import Attribute

class Morph(Attribute):
    """
    Morph Attribute.
    Usage: Morph(...)
    """
    def __init__(self, morphtarget, value):
        self.morphtarget = str(morphtarget)
        self.value = str(value)
