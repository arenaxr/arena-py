"""GLTF Model

Load a GLTF model.

Besides applying standard rotation and position attributes to the center-point of the GLTF model, the individual child components can also be manually manipulated. See format details in the `modelUpdate` data attribute. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

Instantiate a glTF v2.0 binary model (file extension .glb) from a URL.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_xr_logo():
    xr_logo = GLTF(
        object_id="xr-logo",
        position=(0, 0, -3),
        scale=(1.2, 1.2, 1.2),
        url="store/users/wiselab/models/XR-logo.glb",
    )
    scene.add_object(xr_logo)


scene.run_tasks()
