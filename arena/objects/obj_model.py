from .arena_object import Object


class ObjModel(Object):
    """
    ObjModel object class to manage its properties in the ARENA: Loads a 3D model and material using a Wavefront (.OBJ) file and a .MTL file. See guidance to store paths under <https://docs.arenaxr.org/content/interface/filestore.html> ARENA File Store, CDN, or DropBox.

    :param str mtl: Url pointing to a .MTL file. Optional if you wish to use the material component instead. (optional)
    :param str obj: Url pointing to a .OBJ file. Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
    """
    object_type = "obj-model"

    def __init__(self, **kwargs):
        super().__init__(object_type=ObjModel.object_type, **kwargs)
