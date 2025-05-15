from .attribute import Attribute


class PhysxJointConstraint(Attribute):
    """
    PhysxJointConstraint attribute class to manage its properties in the ARENA: Adds a constraint to a physx-joint. Supported joints are D6, Revolute and Prismatic. Can only be used on an entity with the physx-joint component. Requires `scene-options: physics`.
    Usage: `physx_joint_constraint=PhysxJointConstraint(...)`

    :param dict angularLimit: [Revolute] Limit on angular movement in degrees. First component is the minimum allowed angle, second is the maximum. (optional)
    :param list[str] constrainedAxes: [D6] Which axes are constrained by this constraint. These axes can be moved within the set limits. Should be some combination of x, y, z, twist, swing. Defaults to '[]' (optional)
    :param float damping: [All] Spring damping for soft constraints. Defaults to '0' (optional)
    :param list[str] freeAxes: [D6] Which axes are explicitly freed by this constraint. These axes will not obey any limits set here. Should be some combination of x, y, z, twist, swing. Defaults to '[]' (optional)
    :param dict limitCone: [D6] Two angles in degrees specifying a cone in which the joint is allowed to swing, like a pendulum. (optional)
    :param dict linearLimit: [D6, Prismatic] Limit on linear movement. Only affects x, y, and z axes. First component is the minimum allowed position. (optional)
    :param list[str] lockedAxes: [D6] Which axes are explicitly locked by this constraint and can't be moved at all. Should be some combination of x, y, z, twist, swing. Defaults to '[]' (optional)
    :param float restitution: [All] Spring restitution for soft constraints. Defaults to '0' (optional)
    :param float stiffness: [All] If greater than 0, will make this joint a soft constraint, and use a spring force model. Defaults to '0' (optional)
    :param dict twistLimit: [D6] Minimum and maximum angles in degrees that the joint is allowed to twist. (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
