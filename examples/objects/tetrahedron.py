from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_tet():
    my_tet = Tetrahedron(
        object_id="my_tet",
        position=(0,2,-3),
        scale=(2,2,2),
        color=(255,100,255),
    )
    scene.add_object(my_tet)

scene.run_tasks()
