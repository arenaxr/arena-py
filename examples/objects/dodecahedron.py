"""Dodecahedron

Draw a Dodecahedron primitive mesh geometry. Dodecahedron is 12-sided polyhedron shape.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_dodecahedron():
    dod = Dodecahedron(
        object_id="dod",
        position=(0, 2, -3),
        scale=(1, 1, 1),
        material=Material(color=(30, 255, 80)),
    )
    scene.add_object(dod)


scene.run_tasks()
