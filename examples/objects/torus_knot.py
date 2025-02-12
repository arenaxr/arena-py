"""Torus Knot

Torus Knot Geometry.

Instantiate a wacky torusKnot, then turn it blue. Other primitive types are available in the in [A-Frame docs](https://aframe.io/docs/1.5.0/components/geometry.html#built-in-geometries). Here is a brief list: **box circle cone cylinder dodecahedron icosahedron tetrahedron octahedron plane ring sphere torus torusKnot triangle**.

{
  "object_id": "torusKnot_1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "torusKnot",
    "material": { "color": "red" },
    "position": { "x": 0, "y": 1, "z": -4 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 }
  }
}

{
  "object_id": "torusKnot_1",
  "action": "update",
  "type": "object",
  "data": { "material": { "color": "blue" } }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_torusknot():
    my_torusknot = TorusKnot(
        object_id="my_torusknot",
        position=(0, 5, -3),
        scale=(1.5, 1.5, 1.5),
        material=Material(color=(0, 100, 40)),
    )
    scene.add_object(my_torusknot)


scene.run_tasks()
