from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_videosphere():
    my_videosphere = Videosphere(
        object_id="my_videosphere",
        position=(0, 0, 0),
        radius=150,
        src='store/users/wiselab/images/360falls.mp4',
    )
    scene.add_object(my_videosphere)


scene.run_tasks()
