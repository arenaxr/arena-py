from .attribute import Attribute


class DynamicBody(Attribute):
    """
    DynamicBody attribute class to manage its properties in the ARENA: A freely-moving object. Dynamic bodies have mass, collide with other objects, bounce or slow during collisions, and fall if gravity is enabled. More properties at <https://github.com/c-frame/aframe-physics-system/blob/master/CannonDriver.md> A-Frame Physics System.
    Usage: `dynamic_body=DynamicBody(...)`

    :param float angularDamping: Resistance to rotation. Defaults to '0.01' (optional)
    :param str cylinderAxis: Override default axis of bounding cylinder. Requires shape:cylinder. Allows [x, y, z] Defaults to 'y' (optional)
    :param float linearDamping: Resistance to movement. Defaults to '0.01' (optional)
    :param float mass: Simulated mass of the object, > 0. Defaults to '5' (optional)
    :param str shape: Body components will attempt to find an appropriate CANNON.js shape to fit your model. When defining an object you may choose a shape or leave the default, auto. Select a shape carefully, as there are performance implications with different choices. Allows [auto, box, cylinder, sphere, hull, none] Defaults to 'auto' (optional)
    :param float sphereRadius: Override default radius of bounding sphere. Requires shape:sphere. NaN by default. (optional)
    :param str type: Define the result of collisions. Dynamic can be moved, Static cannot be moved. Allows [dynamic, static] Defaults to 'dynamic' (optional)
    """

    def __init__(self, type="static", **kwargs):
        _type = type
        if _type != "static" and _type != "dynamic":
            _type = "none"
        super().__init__(type=_type, **kwargs)


class Physics(DynamicBody):
    """
    Alternate name for DynamicBody.
    Usage: `physics=Physics(...)`
    """
