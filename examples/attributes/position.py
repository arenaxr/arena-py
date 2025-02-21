"""Move

3D object position.

Move the position of an octahedron.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

position = (1, 2, -3)  # Position(1,2,-3) works too


@scene.run_once
def make_moved_octahedron():
    my_oct = Octahedron(
        object_id="my_oct",
        position=position,
    )
    scene.add_object(my_oct)


scene.run_tasks()
