"""Images on Objects

Use the `multisrc` A-Frame Component to specify different bitmaps for sides of a box or other primitive shape.

```json
{
  "object_id": "die1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "box",
    "position": { "x": 0, "y": 0.5, "z": -2 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 },
    "material": { "color": "#ffffff" },
    "dynamic-body": { "type": "dynamic" },
    "multisrc": {
      "srcspath": "store/users/wiselab/images/dice/",
      "srcs": "side1.png,side2.png,side3.png,side4.png,side5.png,side6.png"
    }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_die1():
    die1 = Box(
        object_id="die1",
        position=Position(0, 3,  -2),
        material=Material(color="#ffffff"),
        multisrc=Multisrc(
            srcspath="store/users/wiselab/images/dice/",
            srcs="side1.png,side2.png,side3.png,side4.png,side5.png,side6.png"
        )
    )
    scene.add_object(die1)


scene.run_tasks()
