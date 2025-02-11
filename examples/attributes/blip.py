from arena import *

scene = Scene(host="arenaxr.org", scene="example")

blip = Blip(
    blipin=True,
    blipout=True,
    geometry="disk",
    planes="top",
    duration=500,
)


@scene.run_once
def make_blip_robot():
    blip_robot = GLTF(
        object_id="blip_robot",
        url="/store/models/robot-draco.glb",
        position=Position(-2, 2, -2),
        rotation=Rotation(0.21644, 0, 0, 0.9763),
        material=Material(color="#0084ff", opacity=0.5, transparent=True),
        blip=blip,
    )
    scene.add_object(blip_robot)


scene.run_tasks()
