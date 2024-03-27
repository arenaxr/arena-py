from .attribute import Attribute


class StaticBody(Attribute):
    """
    StaticBody attribute class to manage its properties in the ARENA: A fixed-position or animated object. Other objects may collide with static bodies, but static bodies themselves are unaffected by gravity and collisions. More properties at <https://github.com/c-frame/aframe-physics-system/blob/master/CannonDriver.md> A-Frame Physics System.
    Usage: `static_body=StaticBody(...)`

    :param str cylinderAxis: Override default axis of bounding cylinder. Requires shape:cylinder. Allows [x, y, z] Defaults to 'y' (optional)
    :param str shape: Body components will attempt to find an appropriate CANNON.js shape to fit your model. When defining an object you may choose a shape or leave the default, auto. Select a shape carefully, as there are performance implications with different choices. Allows [auto, box, cylinder, sphere, hull, none] Defaults to 'auto' (optional)
    :param float sphereRadius: Override default radius of bounding sphere. Requires shape:sphere. NaN by default. (optional)
    :param str type: Define the result of collisions. Dynamic can be moved, Static cannot be moved. Allows [dynamic, static] Defaults to 'static' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
