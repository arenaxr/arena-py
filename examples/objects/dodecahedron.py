"""Dodecahedron

Dodecahedron Geometry.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_dod():
    dod = Dodecahedron(
        object_id="dod",
        position=(0, 2, -3),
        scale=(1.5, 1.5, 1.5),
        material=Material(color=(30, 255, 80)),
    )
    scene.add_object(dod)


scene.run_tasks()
