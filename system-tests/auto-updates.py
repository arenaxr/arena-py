# auto-updates.py
#
# Tests automatic updates for objects done by Arena class
# Please run auto-updates-helper.py in another terminal window

from arena import *
import random


scene = Scene(host="arenaxr.org", realm="realm", scene="test")

def evt_handler(scene, evt, msg): # should magically be able to click, thanks to auto-updates-helper.py...
    print("clicked")

def update_handler(obj):
    print(obj.data.position.x)

box = Box(object_id="box", position=Position(0,2,-1), rotation=(0,0,0), scale=Scale(2,2,2), material=Material(transparent=True, opacity=1), evt_handler=evt_handler, update_handler=update_handler)
scene.add_object(box)

scene.update_object(box, click_listener=False)

@scene.run_forever(interval_ms=2000)
def main():
    # note: nothing in this program moves the box to x=10,
    # it is auto-updates-helper.py that moves the box
    if 10 <= box.data.position.x:
        box.data.position.x = 0
        box.data.rotation.x = 0
        box.data.scale.y = 2
        scene.update_object(box)

scene.run_tasks()
