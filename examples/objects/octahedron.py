from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_oct():
    my_oct = Octahedron(
        object_id="my_oct",
        position=(0,2,-3),
        scale=(1.5,1.5,1.5),
        color=(30,100,40),
    )
    scene.add_object(my_oct)

scene.run_tasks()
