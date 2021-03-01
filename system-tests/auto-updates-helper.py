# auto-updates-helper.py
#
# Helper script for auto-updates.py. Tests programs interactions.
# Please run auto-updates.py in another terminal window

from arena import *
import random


scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="test")

box = Box(object_id="box", position=(0,2,-1), rotation=(0,0,0), scale=(2,2,2), material=Material(transparent=True, opacity=1))

@scene.run_forever(interval_ms=1000)
def main():
    box.data.position.x += 1
    box.data.rotation.x += 0.1
    box.data.scale.y -= 0.01
    box.data.material.opacity = (box.data.material.opacity - 0.01) % 1
    print(scene.update_object(
        box,
        click_listener=True,
        # physics=Physics("dynamic"),
        # goto_url=GotoUrl(url="https://wise.ece.cmu.edu/"),

    ))

scene.run_tasks()
