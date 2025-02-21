"""Three.js Scene

Load a Three.js Scene.

Could be THREE.js version-specific; you can see the THREE.js version in the JS console once you open ARENA; using glTF is preferred. Format: <a href='https://threejs.org/docs/#api/en/scenes/Scene'>THREE.js Scene</a>. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_threejs_scene():
    test_scene = ThreejsScene(
        object_id="test-scene",
        position=(0, 1, -3),
        url="/store/users/wiselab/threejs-scenes/simple_scene.json",
    )
    scene.add_object(test_scene)


scene.run_tasks()
