"""Rotate Camera

Rotate cameras around the origin.
"""

import math

from arena import *

radius = 10
interval = 0
sign = 1

def user_join_callback(camera):
    print(f"User found: {camera.displayName} [object_id={camera.object_id}]")


scene = Scene(host="arenaxr.org", scene="test")
scene.user_join_callback = user_join_callback

@scene.run_forever(interval_ms=17)
def move_cams():
    global interval, sign
    for c in scene.users:
        xp = radius*math.cos(interval)
        zp = radius*math.sin(interval)
        scene.manipulate_camera(
            c,
            position=(
                xp,
                3,
                zp,
            ),
            #rotation=Rotation(0,0,0)
        )
        scene.look_at(
            c,
            # target={"x": 0, "y": 0, "z": 0}
            # target=(0, 0, 0)
            target=(xp, 0, zp)
        )
    if interval > 3.14:
        sign = -1
    elif interval < 0:
        sign = 1

    interval = interval + (0.01*sign)


scene.run_tasks()
