from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_rotating_image():
    rotating_image = Image(
        object_id="rotating_image",
        url="store/users/wiselab/images/conix-face-white.jpg",
        position=Position(1, 2, -2),
        look_at="#my-camera",
    )
    scene.add_object(rotating_image)


scene.run_tasks()
