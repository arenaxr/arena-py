from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@scene.run_once
def make_plane():
    my_plane = Plane(
        object_id="my_plane",
        position=(0,5,-3),
        scale=(5,5,5),
        color=(200,200,40),
    )
    scene.add_object(my_plane)

scene.run_tasks()
