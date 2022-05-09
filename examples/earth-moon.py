# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *


def end_program_callback(scene: Scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
scene = Scene(cli_args=True, end_program_callback=end_program_callback)
app_position = scene.args["position"]
app_rotation = scene.args["rotation"]
app_scale = scene.args["scale"]


@scene.run_once
def main():
    global sceneParent
    # make a parent scene object
    sceneParent = Box(
        object_id="earth-sceneParent",
        position=app_position,
        rotation=app_rotation,
        scale=app_scale,
        material=Material(transparent=True, opacity=0),
    )
    scene.add_object(sceneParent)

    # Create models
    earth = GLTF(
        object_id="gltf-model_Earth",
        position=(0, 0.1, 0),
        scale=(10, 10, 10),
        url="store/users/wiselab/models/Earth.glb",
        parent=sceneParent.object_id,
    )
    moon = GLTF(
        object_id="gltf-model_Moon",
        position=(0, 0.05, 0.6),
        scale=(0.05, 0.05, 0.05),
        url="store/users/wiselab/models/Moon.glb",
        parent="gltf-model_Earth",
    )

    scene.add_object(earth)
    scene.add_object(moon)

    # Define animation and movement
    scene.update_object(
        earth,
        animation=Animation(
            property="rotation",
            end=(0, 360, 0),
            loop=True,
            dur=20000,
            easing="linear"
        )
    )
    scene.update_object(
        moon,
        animation=Animation(
            property="scale",
            start=(0.05, 0.05, 0.05),
            end=(0.1, 0.1, 0.1),
            startEvents="click",
            loop=6,
            dur=1000,
            dir="alternate",
            easing="easeInOutCirc"
        ),
        clickable=True
    )
    print(earth.json())

    # Create marker objects
    scene.add_object(Box(object_id="box0", color=Color(
        0, 255, 0), scale=(0.2, 0.2, 0.2), parent=sceneParent.object_id))
    scene.add_object(Box(object_id="box1", color=Color(255, 0, 0), scale=(0.2, 0.2, 0.2),
                         position=(-0.7,  1.67, 2.11), parent=sceneParent.object_id))
    scene.add_object(Box(object_id="box2", color=Color(0, 255, 255), scale=(0.2, 0.2, 0.2),
                         position=(-2.88, 2.80, -2.12), parent=sceneParent.object_id))
    scene.add_object(Box(object_id="box3", color=Color(0, 0, 255), scale=(0.2, 0.2, 0.2),
                         position=(-0.09, 1.30, -3.66), parent=sceneParent.object_id))
    scene.add_object(Box(object_id="box4", color=Color(100, 200, 50), scale=(0.2, 0.2, 0.2),
                         position=(3.31, 2.00, -0.97), parent=sceneParent.object_id))


scene.run_tasks()
