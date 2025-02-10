"""Parent/Child Linking

There is support to attach a child to an already-existing parent scene objects. When creating a child object, set the `"parent": "parent_object_id"` value in the JSON data. For example if parent object is gltf-model_Earth and child object is gltf-model_Moon, the commands would look like:

{
  "object_id": "gltf-model_Earth",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "gltf-model",
    "position": { "x": 0, "y": 0.1, "z": 0 },
    "url": "store/models/Earth.glb",
    "scale": { "x": 5, "y": 5, "z": 5 }
  }
}

{
  "object_id": "gltf-model_Moon",
  "action": "create",
  "type": "object",
  "data": {
    "parent": "gltf-model_Earth",
    "object_type": "gltf-model",
    "position": { "x": 0, "y": 0.05, "z": 0.6 },
    "scale": { "x": 0.05, "y": 0.05, "z": 0.05 },
    "url": "store/models/Moon.glb"
  }
}

Child objects inherit attributes of their parent, for example scale. Scale the parent, the child scales with it. If the parent is already scaled, the child scale will be reflected right away. Child position values are relative to the parent and also scaled.
"""
