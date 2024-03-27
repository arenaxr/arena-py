from .arena_object import Object

class Entity(Object):
    """
    Entity object class to manage its properties in the ARENA: Entities are the base of all objects in the scene. Entities are containers into which components can be attached.

    :param dict geometry: geometry (optional)
    :param dict panel: panel (optional)
    """
    object_type = "entity"

    def __init__(self, **kwargs):
        super().__init__(object_type=Entity.object_type, **kwargs)
