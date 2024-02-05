# rotate-camera.py
#
# Rotate cameras around the origin

import math

from arena import *


radius = 3
interval = 0


def user_join_callback(camera):
    print(f"User found: {camera.displayName} [object_id={camera.object_id}]")


scene = Scene(host="arena-dev1.conix.io", scene="test", debug=True)
scene.user_join_callback = user_join_callback


@scene.run_forever(interval_ms=17)
def move_cams():
    global interval
    for c in scene.users:
        scene.manipulate_camera(
            c,
            position=(
                radius*math.cos(interval),
                3,
                radius*math.sin(interval),
            ),
            # rotation=Rotation(0,0,0)
        )
        scene.look_at(
            c,
            target={"x": 0, "y": 0, "z": 0}
            # target=(0, 0, 0)
        )
    if interval > 6.28:
        interval = 0
    else:
        interval = interval + 0.001


scene.run_tasks()
