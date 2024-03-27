from .arena_object import Object

class ThreejsScene(Object):
    """
    ThreejsScene object class to manage its properties in the ARENA: Load a Three.js Scene. Could be THREE.js version-specific; you can see the THREE.js version in the JS console once you open ARENA; using glTF is preferred. Format: <https://threejs.org/docs/#api/en/scenes/Scene> THREE.js Scene. See guidance to store paths under <https://docs.arenaxr.org/content/interface/filestore.html> ARENA File Store, CDN, or DropBox.

    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
    """
    object_type = "threejs-scene"

    def __init__(self, **kwargs):
        super().__init__(object_type=ThreejsScene.object_type, **kwargs)
