"""Cylinder

Draw a Cylinder primitive mesh geometry. Cylinder is a tube shape with flat ends.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_cylinder():
    my_cylinder = Cylinder(
        object_id="my_cylinder",
        position=(0, 2, -3),
        scale=(1, 2, 1),
        material=Material(color=(255, 100, 16)),
    )
    scene.add_object(my_cylinder)


scene.run_tasks()
