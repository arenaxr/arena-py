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
