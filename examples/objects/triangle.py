from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_triangle():
    my_triangle = Triangle(
        object_id="my_triangle",
        position=(0,5,-3),
        scale=(1.5,1.5,1.5),
        material=Material(color=(10,70,200)),
    )
    scene.add_object(my_triangle)

scene.run_tasks()
