from .attribute import Attribute


class Blip(Attribute):
    """
    Blip attribute class to manage its properties in the ARENA: When the object is created or deleted, it will animate in/out of the scene instead of appearing/disappearing instantly. Must have a geometric mesh.
    Usage: `blip=Blip(...)`

    :param bool applyDescendants: Apply blipout effect to include all descendents. Does not work for blipin. (optional)
    :param bool blipin: Animate in on create, set false to disable. Defaults to 'True' (optional)
    :param bool blipout: Animate out on delete, set false to disable. Defaults to 'True' (optional)
    :param float duration: Animation duration in milliseconds. Defaults to '750' (optional)
    :param str geometry: Geometry of the blipout plane. Allows [rect, disk, ring] Defaults to 'rect' (optional)
    :param str planes: Which which clipping planes to use for effect. A top plane clips above it, bottom clips below it. Allows [both, top, bottom] Defaults to 'both' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
