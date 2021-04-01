from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

material = Material(opacity=0.3, transparent=True)

@scene.run_once
def make_transparent_plane():
    my_plane = Plane(
        object_id="my_plane",
        position=(0,2,-5),
        scale=(4.0,4.0,4.0),
        material=material
    )

    scene.add_object(my_plane)

scene.run_tasks()
