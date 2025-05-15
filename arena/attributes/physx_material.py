from .attribute import Attribute


class PhysxMaterial(Attribute):
    """
    PhysxMaterial attribute class to manage its properties in the ARENA: Controls physics properties for individual shapes or rigid bodies. Can be set on an entity with physx-body or on shapes contained within it. Requires `scene-options: physics`.
    Usage: `physx_material=PhysxMaterial(...)`

    :param list[float] collidesWithLayers: Array containing all layers that this shape should collide with. Defaults to '[1, 2, 3, 4]' (optional)
    :param float collisionGroup: If greater than 0, this shape will not collide with any other shape with the same collisionGroup value. Defaults to '0' (optional)
    :param list[float] collisionLayers: Which collision layers this shape is present on. Defaults to '[1]' (optional)
    :param str contactOffset: If >= 0, sets the PhysX contact offset, indicating how far away from the shape simulation contact events should begin. (optional)
    :param float density: Density for the shape. If specified for all shapes in a rigid body, mass properties will be automatically calculated based on densities. (optional)
    :param float dynamicFriction: Dynamic friction applied when objects are moving relative to each other. Defaults to '0.2' (optional)
    :param str restOffset: If >= 0, sets the PhysX rest offset. (optional)
    :param float restitution: Restitution, or 'bounciness' of the material. Defaults to '0.2' (optional)
    :param float staticFriction: Static friction applied when objects are not moving relative to each other. Defaults to '0.2' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
