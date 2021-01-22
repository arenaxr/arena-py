from ..utils import Utils
from .attribute import Attribute

class Material(Attribute):
    """
    Material Attribute. For setting opacity.
    Usage: material=Material(...)
    """
    def __init__(self, transparent=False, opacity=0, **kwargs):
        opacity = max(0.0, opacity)
        opacity = min(opacity, 1.0)
        super().__init__(transparent=transparent, opacity=Utils.agran(opacity), **kwargs)
