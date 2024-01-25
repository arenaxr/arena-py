from .attribute import Attribute


class Shadow(Attribute):
    """
    Shadow attribute class to manage its properties in the ARENA: 
    Usage: shadow=Shadow(...)
    
    :param bool cast: Whether the entity casts shadows onto the surrounding scene. (optional)
    :param bool receive: Whether the entity receives shadows from the surrounding scene. (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
