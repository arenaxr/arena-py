from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

start = (0,0,-3)
end = (10,10,-10)

@scene.run_once
def make_line():
    line = Line(
        object_id="my_line",
        path=(start, end),
        color=(0,255,0)
    )
    scene.add_object(line)

scene.run_tasks()
