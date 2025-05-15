from .attribute import Attribute


class PhysxJointDriver(Attribute):
    """
    PhysxJointDriver attribute class to manage its properties in the ARENA: Creates a driver which exerts force to return the joint to the initial position with the given velocity characteristics. Can only be used on an entity with a physx-joint component. Currently only supports D6 joint type. Requires `scene-options: physics`.
    Usage: `physx_joint_driver=PhysxJointDriver(...)`

    :param dict angularVelocity: Target angular velocity relative to the joint. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param list[str] axes: Which axes the joint should operate on. Should be some combination of x, y, z, twist, swing. Defaults to '[]' (optional)
    :param float damping: Damping to apply to the drive. Defaults to '1' (optional)
    :param float forceLimit: Maximum amount of force used to get to the target position. Defaults to '3.4028234663852886e+38' (optional)
    :param dict linearVelocity: Target linear velocity relative to the joint. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param bool lockOtherAxes: If true, will automatically lock axes which are not being driven. Defaults to 'False' (optional)
    :param bool slerpRotation: If true, uses SLERP rotation mode. If false, will use SWING mode. Defaults to 'True' (optional)
    :param float stiffness: How stiff the drive should be. Defaults to '1' (optional)
    :param bool useAcceleration: If true, will operate directly on body acceleration rather than on force. Defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
