from arena import *
import random

arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_once
def main():


    def click(evt):
        if evt.type == "mousedown":
            print( "Click!" )
            start = evt.data.clickPos
            end = evt.data.position
            start.y=start.y-.1
            start.x=start.x-.1
            start.z=start.z-.1
            line = ThickLine(path=(start, end), color=(255, 0, 0), lineWidth=5, ttl=1)
            arena.add_object(line)
            ball = Sphere(
                position=end,
                scale = (0.05,0.05,0.05),
                color=(255,0,0),
                ttl=1)
            arena.add_object(ball)
        
    object_id = "screenshare1"
    box = arena.get_persisted_obj(object_id)
    #box.update_attributes(clickable=True)
    box.update_attributes(evt_handler=click)
    arena.update_object(box)

    object_id = "screenshare2"
    box = arena.get_persisted_obj(object_id)
    #box.update_attributes(clickable=True)
    box.update_attributes(evt_handler=click)
    arena.update_object(box)


arena.run_tasks()