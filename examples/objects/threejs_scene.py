from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_test_scene():
    test_scene = ThreejsScene(
        object_id="test-scene",
        position=(0, 1, -3),
        url="/store/users/wiselab/threejs-scenes/simple_scene.json",
    )
    scene.add_object(test_scene)


scene.run_tasks()
