"""Transparent Occlusion

`colorWrite` is an attribute of the THREE.js Shader Material that, by exposing it, we make accessible like others belonging to the Material A-Frame Component, and is an alternative way of controlling visibility. `render-order` is a custom Component that controls which objects are drawn first (not necessarily the same as which are "in front of" others). All other ARENA objects are drawn with render-order of 1.

**This does not occlude the far background A-Frame layer (like environment component stars) but, in AR, that layer is not drawn anyway.**

Define extra material properties, namely texture encoding, whether to render the material's color and render order.

The properties set here access directly Three.js material component.

More properties at <a href='https://threejs.org/docs/#api/en/materials/Material'>THREE.js Material</a>.

Material-extras can traverse objects, so can be applied to a GLTF, e.g:
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

material_extras = MaterialExtras(
    encoding="sRGBEncoding",
    transparentOccluder=True,
)


@scene.run_once
def make_robot():
    robot = GLTF(
        object_id="arobothead",
        url="/store/models/robobit.glb",
        position=(-3, 2, -3),
        scale=(5, 5, 5),
        material_extras=material_extras,
    )
    scene.add_object(robot)


scene.run_tasks()
