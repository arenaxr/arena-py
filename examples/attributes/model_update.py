"""GLTF Model Update

Besides applying standard rotation and position attributes to the center-point of the GLTF model, the individual child components can also be manually manipulated.

The GLTF-specific `modelUpdate` attribute is an object with child component names as keys. The top-level keys are the names of the child components to be updated. The values of each are nested `position` and `rotation` attributes to set as new values, respectively. Either `position` or `rotation` can be omitted if unchanged.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

# joint names might need some characters removed like ':' from 'mixamorig:LeftShoulder'
modelUpdate = {
    "mixamorigLeftShoulder": {
        "position": {"x": 1, "y": 0, "z": 0},
        "rotation": {"x": 1, "y": 0, "z": 0, "w": 0},
    },
    "mixamorigRightLeg": {
        "rotation": {"x": -0.7, "y": 0, "z": 0, "w": 0.7},
    },
}


@scene.run_once
def make_model_update():
    model_update = GLTF(
        object_id="model_update_draco",
        position=(0, 2, -3),
        url="/store/models/robot-draco.glb",
        modelUpdate=modelUpdate,
    )
    scene.add_object(model_update)


scene.run_tasks()
