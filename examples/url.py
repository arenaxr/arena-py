# url.py
#
from arena import *

arena = Arena("arena.andrew.cmu.edu", "example", "realm")

print("Three clickable URL cubes targetted to different windows" )

popup = Cube(
    position=(-3, 0, -5),
    color=(255,0,0),
    click_listener=True,
    goto_url=GotoUrl(dest="popup", on="mousedown", url="https://www.conix.io/")
)

newtab = Cube(
    position=(0, 0, -5),
    color=(0,255,0),
    click_listener=True,
    goto_url=GotoUrl(dest="newtab", on="mousedown", url="https://wise.ece.cmu.edu/")
)

sametab = Cube(
    position=(3, 0, -5),
    color=(0,0,255),
    click_listener=True,
    goto_url=GotoUrl(dest="sametab", on="mousedown", url="https://www.ece.cmu.edu/")
)


@arena.run_once
def add_objs():
    arena.add_object(popup)
    arena.add_object(newtab)
    arena.add_object(sametab)


arena.start_tasks()
