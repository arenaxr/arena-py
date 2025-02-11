from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_bunny_pcd():
    bunny_pcd = PcdModel(
        object_id="bunny_pcd",
        position=(0, 1, -3),
        scale=(5, 5, 5),
        pointSize=0.01,
        pointColor="#7f7f7f",
        url="/store/users/wiselab/pcd-models/bunny.pcd",
    )
    scene.add_object(bunny_pcd)


scene.run_tasks()
