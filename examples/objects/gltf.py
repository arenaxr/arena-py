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
