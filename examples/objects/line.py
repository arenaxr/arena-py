from arena import *

scene = Scene(host="arenaxr.org", scene="example")

start = (0,0,-3)
end = (5,5,5)

@scene.run_once
def make_line():
    line = Line(
        object_id="my_line",
        start=start,
        end=end,
        color=(0,255,0)
    )

scene.run_tasks()
