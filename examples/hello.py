from arena import *

arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_once
def make_box():
    arena.add_object(Box())

arena.run_tasks()
