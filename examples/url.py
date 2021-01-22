# url.py
#
from arena import *

arena = Arena("arena.andrew.cmu.edu", "realm", "public", "example")

print("Three clickable URL boxs targetted to different windows" )

popup = Box(
    position=(-3, 0, -5),
    color=(255,0,0),
    clickable=True,
    goto_url=GotoUrl(dest="popup", on="mousedown", url="https://www.conix.io/")
)

newtab = Box(
    position=(0, 0, -5),
    color=(0,255,0),
    clickable=True,
    goto_url=GotoUrl(dest="newtab", on="mousedown", url="https://wise.ece.cmu.edu/")
)

sametab = Box(
    position=(3, 0, -5),
    color=(0,0,255),
    clickable=True,
    goto_url=GotoUrl(dest="sametab", on="mousedown", url="https://www.ece.cmu.edu/")
)


@arena.run_once
def add_objs():
    arena.add_object(popup)
    arena.add_object(newtab)
    arena.add_object(sametab)


arena.run_tasks()
