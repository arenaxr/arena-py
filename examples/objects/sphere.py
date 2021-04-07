from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

@scene.run_once
def make_sphere():
    my_sphere = Sphere(
        object_id="my_sphere",
        position=(0,2,-3),
        scale=(1.5,1.5,1.5),
        color=(0,255,255),
    )
    scene.add_object(my_sphere)

scene.run_tasks()
