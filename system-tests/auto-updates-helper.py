# auto-updates-helper.py
#
# helper script for auto-updates.py. Tests programs interactions.

from arena import *
import random


arena = Arena("arena.andrew.cmu.edu", "realm", "test")

cube = Cube(object_id="cube", position=Position(0,2,-1), rotation=(0,0,0), scale=Scale(2,2,2))

o = 1
@arena.run_forever(interval_ms=1000)
def main():
    global o

    cube.data.position.x += 1
    cube.data.rotation.x += 0.1
    cube.data.scale.y -= 0.01
    print(arena.update_object(
        cube,
        click_listener=True,
        # physics=Physics("dynamic"),
        goto_url=GotoUrl(url="https://www.google.com"),
        material=Material(transparent=True, opacity=o)
    ))
    o = (o - 0.01) % 1

arena.start_tasks()
