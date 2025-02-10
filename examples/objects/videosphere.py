"""360 Video

Draw a sphere, set the texture src to be an equirectangular video, on the 'back' (inside).

{
  "object_id": "sphere_vid",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "sphere",
    "scale": { "x": 200, "y": 200, "z": 200 },
    "rotation": { "x": 0, "y": 0.7, "z": 0, "w": 0.7 },
    "material": { "color": "#808080" },
    "material": { "src": "images/360falls.mp4", "side": "back" }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_videosphere():
    my_videosphere = Videosphere(
        object_id="my_videosphere",
        position=(0, 0, 0),
        radius=150,
        src='store/users/wiselab/images/360falls.mp4',
    )
    scene.add_object(my_videosphere)


scene.run_tasks()
