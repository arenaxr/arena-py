"""Icosahedron

Draw a Icosahedron primitive mesh geometry. Icosahedron is 20-sided polyhedron shape.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_iso():
    iso = Icosahedron(
        object_id="iso",
        position=(0, 2, -3),
        scale=(1.5, 1.5, 1.5),
        material=Material(color=(10, 60, 255)),
    )
    scene.add_object(iso)


scene.run_tasks()
