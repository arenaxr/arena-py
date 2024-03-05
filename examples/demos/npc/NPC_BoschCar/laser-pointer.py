from arena import *
import random

scene = Scene(host="arenaxr.org", namespace = "johnchoi", scene="NPC")

def click(scene, evt, msg):
    if evt.type == "mousedown":
        # print("Click!")
        start = evt.data.clickPos
        end = evt.data.position
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
        if obj.clickable:
            obj.update_attributes(evt_handler=click)
            scene.update_object(obj)
            print(obj)

scene.run_tasks()
