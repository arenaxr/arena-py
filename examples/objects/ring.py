"""Ring

Draw a Ring primitive mesh geometry. Ring is flat rounded shape with 2 edges, inner and outer.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_ring():
    my_ring = Ring(
        object_id="my_ring",
        position=(0, 2, -3),
        scale=(1, 1, 1),
        material=Material(color=(255, 0, 255)),
    )
    scene.add_object(my_ring)


scene.run_tasks()
