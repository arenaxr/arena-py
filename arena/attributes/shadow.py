from .attribute import Attribute


class Shadow(Attribute):
    """
    Shadow attribute class to manage its properties in the ARENA: The shadow component enables shadows for an entity and its children. Adding the shadow component alone is not enough to display shadows in your scene. We must have at least one light with castShadow: true enabled.
    Usage: `shadow=Shadow(...)`

    :param bool cast: Whether the entity casts shadows onto the surrounding scene. (optional)
    :param bool receive: Whether the entity receives shadows from the surrounding scene. (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
