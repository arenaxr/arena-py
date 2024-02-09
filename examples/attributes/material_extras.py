from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_robot():
    robot = GLTF(
        object_id="arobothead",
        url="/store/models/robobit.glb",
        position=(-3, 2, -3),
        scale=(5, 5, 5),
        material_extras=MaterialExtras(
            encoding="sRGBEncoding",
            transparentOccluder=True,
        )
    )
    scene.add_object(robot)


scene.run_tasks()
