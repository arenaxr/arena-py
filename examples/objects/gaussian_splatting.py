"""3D Gaussian Splat

Load a 3D Gaussian Splat for Real-Time Radiance Field Rendering.

More information: <a href='https://github.com/quadjr/aframe-gaussian-splatting'>A-Frame Gaussian Splatting</a>. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_seal_splat():
    seal_splat = GaussianSplatting(
        object_id="seal_splat",
        position=(0, 0.5, -3),
        src="/store/splats/luma-seal.splat",
    )
    scene.add_object(seal_splat)


scene.run_tasks()
