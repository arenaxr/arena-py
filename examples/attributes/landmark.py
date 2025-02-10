"""Landmark

Creates a landmark that can be teleported to from the UI list, or is one of the random starting positions for the scene

{
  "object_id": "box_1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "position": { "x": 1, "y": 1, "z": -1 },
    "landmark": {
      "label": "Box 1",
      "randomRadiusMin": 1,
      "randomRadiusMax": 2,
      "lookAtLandmark": true
    }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

object_id = "the_box"


@scene.run_once
def make_box():
    scene.add_object(
        Box(
            object_id=object_id,
            position=(0, 2, -2),
            landmark=Landmark(label="The Box")
        )
    )


scene.run_tasks()
