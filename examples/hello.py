from arena import Arena, Cube

arena = Arena("arena.andrew.cmu.edu", "realm", "example")

@arena.run_once
def make_cube():
    arena.add_object(Cube())

arena.start_tasks()
