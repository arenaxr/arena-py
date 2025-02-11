"""Impulse

One physics feature is applying an impulse to an object to set it in motion. This happens in conjunction with an event. As an example, here are messages setting objects fallBox and fallBox2 to respond to `mouseup` and `mousedown` messages with an impulse with a certain force and position.

{
  "object_id": "fallBox2",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "dynamic-body": { "type": "dynamic" },
    "impulse": { "on": "mousedown", "force": "1 50 1", "position": "1 1 1" },
    "click-listener": "",
    "position": { "x": 0.1, "y": 4.5, "z": -4 },
    "scale": { "x": 0.5, "y": 0.5, "z": 0.5 }
  }
}

{
  "object_id": "fallBox",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "dynamic-body": { "type": "dynamic" },
    "impulse": { "on": "mouseup", "force": "1 50 1", "position": "1 1 1" },
    "click-listener": "",
    "position": { "x": 0, "y": 4, "z": -4 },
    "scale": { "x": 0.5, "y": 0.5, "z": 0.5 }
  }
}
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_bouncy_ball():
    obj = Sphere(
        clickable=True,
        physics=Physics(type="dynamic"),
        impulse=Impulse(position=(1,1,1), force=(1,50,1)),
        position=(0,5,0))

    scene.add_object(obj)

scene.run_tasks()
