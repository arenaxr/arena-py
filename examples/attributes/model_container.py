"""Model Container

Overrides absolute size for a 3D model. The model can be a glTF, glb, obj, or any other supported format. The model will be rescaled to fit to the sizes specified for each axes.

This example scales the Duck model into a 10 x 10 x 10 box.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

model_container = ModelContainer(
    x=10,
    y=10,
    z=10,
)


@scene.run_once
def make_model_container():
    scene.add_object(
        GltfModel(
            object_id="gltf-model-duck",
            url="store/models/Duck.glb",
            position=(0, 1, -5),
            model_container=model_container,
            persist=True,
        )
    )


scene.run_tasks()
