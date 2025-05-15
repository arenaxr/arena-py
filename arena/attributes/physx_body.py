from .attribute import Attribute


class PhysxBody(Attribute):
    """
    PhysxBody attribute class to manage its properties in the ARENA: Turns an entity into a PhysX rigid body. This is the main component for creating physics objects. There are 3 types of rigid bodies: dynamic objects that have physics simulated on them, static objects that cannot move, and kinematic objects that can be moved programmatically but not by simulation. Requires `scene-options: physics`.
    Usage: `physx_body=PhysxBody(...)`

    :param float angularDamping: If > 0, will set the rigid body's angular damping to reduce rotation over time. Defaults to '0' (optional)
    :param bool emitCollisionEvents: If set to true, it will emit 'contactbegin' and 'contactend' events when collisions occur. Defaults to 'False' (optional)
    :param bool highPrecision: If set to true, the object will receive extra attention by the simulation engine (at a performance cost). Defaults to 'False' (optional)
    :param float linearDamping: If > 0, will set the rigid body's linear damping to reduce movement over time. Defaults to '0' (optional)
    :param float mass: Total mass of the body. Defaults to '1' (optional)
    :param dict shapeOffset: Offset applied to generated collision shapes. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param str type: Type of the rigid body to create. Dynamic can be moved by physics, Static cannot be moved, Kinematic can be moved programmatically. Allows [dynamic, static, kinematic] Defaults to 'dynamic' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
