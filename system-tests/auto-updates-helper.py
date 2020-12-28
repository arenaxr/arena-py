# auto-updates-helper.py
#
# helper script for auto-updates.py. Tests programs interactions.

from arena import *
import random


arena = Arena("arena.andrew.cmu.edu", "realm", "test")

cube = Cube(object_id="cube", position=(0,2,-1), rotation=(0,0,0), scale=(2,2,2), material=Material(transparent=True, opacity=1))

@arena.run_forever(interval_ms=1000)
def main():
    cube.data.position.x += 1
    cube.data.rotation.x += 0.1
    cube.data.scale.y -= 0.01
    cube.data.material.opacity = (cube.data.material.opacity - 0.01) % 1
    print(arena.update_object(
        cube,
        click_listener=True,
        # physics=Physics("dynamic"),
        goto_url=GotoUrl(url="https://wise.ece.cmu.edu/"),

    ))

arena.run_tasks()
