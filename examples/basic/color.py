"""Color

Change only the color of the already-drawn box.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

color = (100, 200, 100)  # Color(100,200,100) works too


@scene.run_once
def make_colored_iso():
    my_iso = Icosahedron(
        object_id="my_iso",
        position=(0, 2, -5),
        material=Material(color=color),
    )
    scene.add_object(my_iso)


scene.run_tasks()
