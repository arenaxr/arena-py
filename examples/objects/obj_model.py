from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_vr_controller_vive():
    vr_controller_vive = ObjModel(
        object_id="vr_controller_vive",
        position=(0, 2, -3),
        scale=(7, 7, 7),
        obj="store/models/vr_controller_vive.obj",
        mtl="store/models/vr_controller_vive.mtl",
    )
    scene.add_object(vr_controller_vive)


scene.run_tasks()
