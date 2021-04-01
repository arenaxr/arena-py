from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@scene.run_once
def make_torusknot():
    my_torusknot = TorusKnot(
        object_id="my_torusknot",
        position=(0,5,-3),
        scale=(1.5,1.5,1.5),
        color=(0,100,40),
    )
    scene.add_object(my_torusknot)

scene.run_tasks()
