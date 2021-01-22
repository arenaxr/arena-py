from arena import *

arena = Arena("arena.andrew.cmu.edu", "realm", "public", "example")

@arena.run_once
def make_box():
    arena.add_object(Box())

arena.run_tasks()
