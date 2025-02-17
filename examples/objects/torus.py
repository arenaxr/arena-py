"""Torus

Draw a Torus primitive mesh geometry. Torus is a tube shaped into a circle.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_torus():
    my_torus = Torus(
        object_id="my_torus",
        position=(0, 5, -3),
        scale=(0.5, 0.5, 0.5),
        material=Material(color=(100, 70, 40)),
    )
    scene.add_object(my_torus)


scene.run_tasks()
