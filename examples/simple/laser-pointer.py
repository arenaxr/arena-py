"""Laser Pointer
"""

import random

from arena import *

scene = Scene(host="arenaxr.org", scene="test")

def click(scene, evt, msg):
    if evt.type == "mousedown":
        # print("Click!")
        start = evt.data.originPosition
        end = evt.data.targetPosition
        start.y=start.y-.1
        start.x=start.x-.1
        start.z=start.z-.1
        line = ThickLine(path=(start,end), color=(255,0,0), lineWidth=5, ttl=1)
        scene.add_object(line)
        ball = Sphere(
            position=end,
            scale = (0.06,0.06,0.06),
            color=(255,0,0),
            ttl=1)
        scene.add_object(ball)

@scene.run_once
def main():
    objs = scene.get_persisted_objs()
    for obj_id,obj in objs.items():
        # obj.update_attributes(clickable=True)
        try:
            if obj.clickable:
                obj.update_attributes(evt_handler=click)
                scene.update_object(obj)
                print("Clickable: ", obj_id)
        except AttributeError:
            print("Skipped: ", obj_id)
            pass

scene.run_tasks()
