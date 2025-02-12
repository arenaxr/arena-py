"""Parent/Child Linking

Child objects inherit attributes of their parent, for example scale. Scale the parent, the child scales with it. If the parent is already scaled, the child scale will be reflected right away. Child position values are relative to the parent and also scaled.

There is support to attach a child to an already-existing parent scene objects. When creating a child object, set the `"parent": "parent_object_id"` value in the JSON data. For example if parent object is gltf-model_Earth and child object is gltf-model_Moon, the commands would look like:
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="earth")

earth = GLTF(
    object_id="gltf-model_Earth",
    scale=(5, 5, 5),
    url="store/users/wiselab/models/Earth.glb",
    persist=True,
)
moon = GLTF(
    object_id="gltf-model_Moon",
    position=(0, 0.05, 0.6),
    scale=(0.05, 0.05, 0.05),
    url="store/users/wiselab/models/Moon.glb",
    persist=True,
    parent="gltf-model_Earth",
)
scene.add_objects([earth, moon])
scene.run_tasks()
