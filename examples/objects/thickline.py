from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

start = (0,0,-3)
end = (10,10,-10)

@scene.run_once
def make_thickline():
    thickline = ThickLine(
        object_id="my_thickline",
        lineWidth=20,
        path=(start, end),
        color=(0,255,0)
    )
    scene.add_object(thickline)

scene.run_tasks()
