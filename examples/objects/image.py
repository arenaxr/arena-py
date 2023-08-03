from arena import *

scene = Scene(host="arenaxr.org", scene="example")

image_url = "store/users/wiselab/images/conix-face-white.jpg"

@scene.run_once
def make_im():
    im = Image(
        object_id="im",
        position=(0,2,-3),
        scale=(1.2,1.5,1.2),
        url=image_url
    )

scene.run_tasks()
