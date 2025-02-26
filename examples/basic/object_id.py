"""Object Naming

"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_named_boxes():
    # create a box with a uuid generated name
    box_named_id = Box(
        object_id="box1",
    )
    scene.add_object(box_named_id)

    # create a box with the name "box1"
    box_named_uuid = Box()
    scene.add_object(box_named_uuid)


scene.run_tasks()
