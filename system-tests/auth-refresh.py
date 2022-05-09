# auth-refresh.py
#
# Tests ability for MQTT connection to accept updated credentials.

import random

from arena import *
from arena import auth

scene = Scene(host="localhost", scene="test")
idx = 0


@scene.run_forever(interval_ms=1000)
def main():
    global idx
    scene.update_object(
        Box(object_id=f"box{idx}", position=(idx, 2, -1), rotation=(0, 0, 0), ttl=60,
            scale=(1, 1, 1), material=Material(transparent=True, opacity=0.5)),
        click_listener=True,
    )
    print(idx)
    idx = idx+1


scene.run_tasks()
