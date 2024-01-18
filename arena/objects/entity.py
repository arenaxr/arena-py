from .arena_object import Object

class Entity(Object):
    """
    Class for Entity in the ARENA: Entities are the base of all objects in the scene. Entities are containers into which components can be attached.
    
    :param dict geometry:  (optional)
    :param dict panel:  (optional)
    """
    object_type = "entity"

    def __init__(self, **kwargs):
        super().__init__(object_type=Entity.object_type, **kwargs)
