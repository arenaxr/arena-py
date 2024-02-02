from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_circle():
    my_circle = Circle(
        object_id="my_circle",
        position=(0,2,-3),
        rotation=(-45,0,0),
        scale=(1.5,1.5,1.5),
        material=Material(color=(70,0,100)),
    )
    scene.add_object(my_circle)

scene.run_tasks()
