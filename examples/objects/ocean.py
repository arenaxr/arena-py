"""Ocean

Draw an Ocean primitive. Ocean is flat shape with 4 edges, in which the inner triangles are animated to mimic ocean waves.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_box():
    my_ocean = Ocean(
        object_id="my_ocean",
        position=(0, 0.5, -3),
        rotation=(-90, 0, 0),
        width=10,
        depth=10,
    )
    scene.add_object(my_ocean)


scene.run_tasks()
