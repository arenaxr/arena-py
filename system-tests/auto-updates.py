# auto-updates.py
#
# Tests automatic updates for objects done by Arena class

from arena import *
import random


arena = Arena("arena.andrew.cmu.edu", "realm", "test")

def evt_handler(evt):
    print("clicked")

cube = Cube(object_id="cube", position=Position(0,2,-1), rotation=(0,0,0), scale=Scale(2,2,2), evt_handler=evt_handler)
arena.add_object(cube)

arena.update_object(cube, click_listener=False)

@arena.run_forever(interval_ms=2000)
def main():
    print(cube.json())

arena.start_tasks()
