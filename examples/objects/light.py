"""Lights

Create a red light in the scene.

{
  "object_id": "light_3",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "light",
    "position": { "x": 1, "y": 1, "z": 1 },
    "rotation": { "x": 0.25, "y": 0.25, "z": 0, "w": 1 },
    "color": "#FF0000"
  }
}

Default is ambient light. To change type, or other light [A-Frame Light](https://aframe.io/docs/0.9.0/components/light.html) parameters, example: change to **directional**. Options: **ambient, directional, hemisphere, point, spot**.

{
  "object_id": "light_3",
  "action": "update",
  "type": "object",
  "data": { "object_type": "light", "type": "directional" }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_light():
    light = Light(
        object_id="my_light",
        type="point",
        position=(0,2,-3),
        rotation=(0.25,0.25,0,1),
        scale=(1.5,1.5,1.5),
        color=(255,0,0)
    )
    scene.add_object(light)

scene.run_tasks()
