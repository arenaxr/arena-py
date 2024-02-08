from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_model_update():
    model_update = GLTF(
        object_id="model_update_draco",
        position=(0, 2, -3),
        url="/store/models/robot-draco.glb",
        modelUpdate={
            "mixamorig:LeftShoulder": {
                "position": {"x": 1, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 1, "z": 0, "w": 0}
            },
            "mixamorig:RightShoulder": {
                "rotation": {"x": -1, "y": 0, "z": 0, "w": 0}
            },
        },
        # TODO (mwfarb): neither of these examples seems to work
        # url="store/models/BrainStem.glb",
        # modelUpdate={
        #     "joint4": {
        #         "position": {"x": 1, "y": 0, "z": 0},
        #         "rotation": {"x": 0, "y": 1, "z": 0, "w": 0}
        #     },
        #     "joint6": {
        #         "rotation": {"x": -1, "y": 0, "z": 0, "w": 0}
        #     },
        # },
    )
    scene.add_object(model_update)


scene.run_tasks()
