"""Draw a Box

Instantiate a box and set all of it's basic parameters.

{
  "object_id": "box_1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "position": { "x": 1, "y": 1, "z": -1 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 },
    "material": { "color": "#FF0000" }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_box():
    my_box = Box(
        object_id="my_box",
        position=(0,2,-3),
        scale=(1.5,1.5,1.5),
        color=(50,60,200),
    )
    scene.add_object(my_box)

scene.run_tasks()
