from .arena_object import Object

class PcdModel(Object):
    """
    Class for PcdModel in the ARENA: Load a PCD model.  Format: (https://pointclouds.org/documentation/tutorials/index.html) Point Clouds. See guidance to store paths under (https://docs.arenaxr.org/content/interface/filestore.html) ARENA File Store, CDN, or DropBox.
    
    :param str url: Store File Store file paths under 'store/users/<username>', see CDN and other storage options in the description above. (optional)
    :param float pointSize: Size of the points; defaults to '0.01' (optional)
    :param str pointColor: Color of the points; defaults to '#7f7f7f' (optional)
    """
    object_type = "pcd-model"

    def __init__(self, **kwargs):
        super().__init__(object_type=PcdModel.object_type, **kwargs)
