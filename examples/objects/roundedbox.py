"""Rounded Box

Draw a Rounded Box primitive mesh geometry. Rounded Box is 6-sided polyhedron shape with rounded edges.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_box():
    my_box = Roundedbox(
        object_id="my_box",
        position=(0, 2, -3),
        scale=(1, 1, 1),
        material=Material(color=(50, 60, 200)),
        radius=0.25,
    )
    scene.add_object(my_box)


scene.run_tasks()
