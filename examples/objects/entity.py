from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_box():
    my_ent = Entity(
        object_id="invisible_object",
        position=(0,2,-3),
    )
    scene.add_object(my_ent)

scene.run_tasks()
