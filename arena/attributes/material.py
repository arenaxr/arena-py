from ..utils import Utils
from .attribute import Attribute

class Material(Attribute):
    """
    Material Attribute. For setting color and opacity.
    Usage: material=Material(...)
    """
    def __init__(self, **kwargs):
        if "opacity" in kwargs:
            # kwargs["transparent"] = True # need to be transparent to be opaque
            if kwargs["opacity"] > 1.0: # keep opacity between 0.0 and 1.0
                kwargs["opacity"] = float(kwargs["opacity"]) / 100
            kwargs["opacity"] = max(0.0, kwargs["opacity"])
            kwargs["opacity"] = min(kwargs["opacity"], 1.0)

        super().__init__(**kwargs)
