# move-camera.py
#
# Move cameras to a random location

from arena import *
import random

def rando():
    return float(random.randint(-100000, 100000)) / 1000


def user_join_callback(camera):
    print(f"User found: {camera.displayName} [object_id={camera.object_id}]")


scene = Scene(host="arenaxr.org", realm="realm", scene="test")
scene.user_join_callback = user_join_callback

# box = Box(object_id="box")
# scene.add_object(box)

@scene.run_forever(interval_ms=500)
def move_cams():
    for c in scene.users:
        scene.manipulate_camera(
            c,
            position=(rando(),1.6,rando()),
            rotation=(0,0,0,1)
        )
        scene.look_at(
            c,
            target=(0,0,0)
        )


scene.run_tasks()
