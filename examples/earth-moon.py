# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *

arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_once
def main():
    # Create models
    earth = GLTF(
            object_id="gltf-model_Earth",
            position=(0, 0.1, 0),
            scale=(10, 10, 10),
            url="models/Earth.glb"
        )
    moon = GLTF(
            object_id="gltf-model_Moon",
            position=(0, 0.05, 0.6),
            scale=(0.05, 0.05, 0.05),
            url="models/Moon.glb",
            parent="gltf-model_Earth"
        )

    arena.add_object(earth)
    arena.add_object(moon)

    ## Define animation and movement
    arena.update_object(
        earth,
        animation=Animation(
            property="rotation",
            end=(0,360,0),
            loop=True,
            dur=20000,
            easing="linear"
        )
    )
    arena.update_object(
        moon,
        animation=Animation(
            property="scale",
            start=(0.05, 0.05, 0.05), end=(0.1,0.1,0.1),
            startEvents="click",
            loop=6,
            dur=1000,
            dir="alternate",
            easing="easeInOutCirc"
        ),
        clickable=True
    )
    print(earth.json())

    ## Create marker objects
    arena.add_object(Box(object_id="box0", material=Material(color=(0,255,0)), scale=(0.2, 0.2, 0.2)))
    arena.add_object(Box(object_id="box1", material=Material(color=(255,0,0)), scale=(0.2, 0.2, 0.2),
                            position=(-0.7,  1.67, 2.11)))
    arena.add_object(Box(object_id="box2", material=Material(color=(0,255,255)), scale=(0.2, 0.2, 0.2),
                            position=(-2.88, 2.80, -2.12)))
    arena.add_object(Box(object_id="box3", material=Material(color=(0,0,255)), scale=(0.2, 0.2, 0.2),
                            position=(-0.09, 1.30, -3.66)))
    arena.add_object(Box(object_id="box4", material=Material(color=(100,200,50)), scale=(0.2, 0.2, 0.2),
                            position=(3.31, 2.00, -0.97)))

arena.run_tasks()
