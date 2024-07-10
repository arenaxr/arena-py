from .arena_object import Object


class UrdfModel(Object):
    """
    UrdfModel object class to manage its properties in the ARENA: Load a URDF model. See guidance to store paths under <https://docs.arenaxr.org/content/interface/filestore.html> ARENA File Store, CDN, or DropBox.

    :param str joints: Set joint values (in degrees) in the form 'JointName1: ValueInDegrees1, JointName2: ValueInDegrees2, ...'.  (optional)
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
    :param str urlBase: Base path for xacro/urdf package includes. This must be an absolute path with no trailing slash, e.g. '/store/users/username/robot' (optional)
    """
    object_type = "urdf-model"

    def __init__(self, **kwargs):
        super().__init__(object_type=UrdfModel.object_type, **kwargs)
