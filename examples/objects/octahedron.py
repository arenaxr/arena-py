"""Octahedron

Draw a Octahedron primitive mesh geometry. Octahedron is 8-sided polyhedron shape.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_octahedron():
    my_oct = Octahedron(
        object_id="my_oct",
        position=(0, 2, -3),
        scale=(1, 1, 1),
        material=Material(color=(30, 100, 40)),
    )
    scene.add_object(my_oct)


scene.run_tasks()
