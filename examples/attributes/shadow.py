"""Shadow
Shadow
The shadow component enables shadows for an entity and its children. Adding the shadow component alone is not enough to display shadows in your scene. We must have at least one light with castShadow: true enabled.

IMPORTANT: Adding the shadow component alone is not enough to display shadows in your scene. We must have at least one light with castShadow: true enabled.
Additionally, the light’s shadow camera (used for depth projection) usually must be configured correctly. Refer to the light component for more information: https://aframe.io/docs/1.5.0/components/shadow.html.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

shadow = Shadow(
    cast=True,
    receive=True,
)


@scene.run_once
def make_shadow_model():
    shadow_model = GLTF(
        object_id="shadow_model",
        url="/store/models/robot-draco.glb",
        position=Position(0, 1, -2),
        shadow=shadow,
    )
    scene.add_object(shadow_model)

    shadow_plane = Plane(
        object_id="shadow_plane",
        position=Position(0, 0.1, 0),
        rotation=Rotation(-90, 0, 0),
        scale=Scale(100, 100, 100),
        shadow=shadow,
    )
    scene.add_object(shadow_plane)

    shadow_light = Light(
        object_id="shadow_light",
        position=Position(10, 10, 10),
        castShadow=True,
        type="point",
    )
    scene.add_object(shadow_light)


scene.run_tasks()
