"""Move

Move the position of the already drawn box.

{
  "object_id": "box_1",
  "action": "update",
  "type": "object",
  "data": { "position": { "x": 2, "y": 2, "z": -1 } }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

position = (1,2,-3) # Position(1,2,-3) works too

@scene.run_once
def make_oct():
    my_oct = Octahedron(
        object_id="my_oct",
        position=position
    )

    scene.add_object(my_oct)

scene.run_tasks()
