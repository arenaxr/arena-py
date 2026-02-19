"""Hello World
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_box():
    scene.add_object(Cube())

scene.run_tasks()
