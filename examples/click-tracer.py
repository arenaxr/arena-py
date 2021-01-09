from arena import *

arena = Arena("arena.andrew.cmu.edu", "realm", "example")

@arena.run_once
def main():
    def click(evt):
        if evt.type == "mousedown":
            start = evt.data.clickPos
            end = evt.data.position
            line = ThickLine(path=(start, end), lineWidth=5)
            print(arena.add_object(line))

    cube = Cube(object_id="my_cube", persist=True, color=(255,0,0), position=Position(0,0,0), scale=Scale(0.05,0.05,0.05), click_listener=True, evt_handler=click)
    arena.add_object(cube)

arena.run_tasks()
