from .attribute import Attribute


class PhysxJoint(Attribute):
    """
    PhysxJoint attribute class to manage its properties in the ARENA: Creates a PhysX joint between an ancestor rigid body and a target rigid body. Position and rotation of the entity will be used to create the corresponding joint. Requires `scene-options: physics`.
    Usage: `physx_joint=PhysxJoint(...)`

    :param dict breakForce: Force needed to break the constraint. First component is linear force, second is angular force in degrees. Set both components >= 0 to enable. Defaults to '{'x': -1, 'y': -1}' (optional)
    :param bool collideWithTarget: If false, collision will be disabled between the rigid body containing the joint and the target rigid body. Defaults to 'False' (optional)
    :param dict projectionTolerance: Kinematic projection, which forces joint back into alignment when the solver fails. First component is linear tolerance in meters, second is angular tolerance in degrees. Defaults to '{'x': -1, 'y': -1}' (optional)
    :param bool removeElOnBreak: If true, removes the entity containing this component when the joint is broken. Defaults to 'False' (optional)
    :param bool softFixed: When used with a D6 type, sets up a 'soft' fixed joint. E.g., for grabbing things. Defaults to 'False' (optional)
    :param str target: Target object selector. Must be an entity having the physx-body component. If not specified, joins to the initial position in the world. (optional)
    :param str type: Rigid body joint type to use. Each type has different movement constraints. Allows [Spherical, Fixed, Revolute, Prismatic, D6] Defaults to 'Spherical' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
