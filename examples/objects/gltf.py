"""Models

Instantiate a glTF v2.0 binary model (file extension .glb) from a URL.

{
  "object_id": "gltf-model_1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "gltf-model",
    "url": "https://arenaxr.org/models/Duck.glb",
    "position": { "x": 0, "y": 1, "z": -4 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_xr_logo():
    xr_logo = GLTF(
        object_id="xr-logo",
        position=(0,0,-3),
        scale=(1.2,1.2,1.2),
        url="store/users/wiselab/models/XR-logo.glb",
    )
    scene.add_object(xr_logo)

scene.run_tasks()
