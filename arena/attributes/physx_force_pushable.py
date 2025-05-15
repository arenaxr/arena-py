from .attribute import Attribute


class PhysxForcePushable(Attribute):
    """
    PhysxForcePushable attribute class to manage its properties in the ARENA: Makes a physx-body object pushable by the user. Requires `click-listener` attribute. Requires `scene-options: physics`.
    Usage: `physx_force_pushable=PhysxForcePushable(...)`

    :param float force: Force to apply to the object. Defaults to '10' (optional)
    :param str on: Event to listen 'on'. Allows [mousedown, mouseup] Defaults to 'mousedown' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
