"""Ring

Ring Geometry.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_ring():
    my_ring = Ring(
        object_id="my_ring",
        position=(0, 2, -3),
        scale=(1.5, 1.5, 1.5),
        material=Material(color=(255, 0, 255)),
    )
    scene.add_object(my_ring)


scene.run_tasks()
