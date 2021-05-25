# url.py
#
from arena import *

scene = Scene(host="arenaxr.org", scene="example")

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


@scene.run_once
def make_urls():
    scene.add_object(popup)
    scene.add_object(newtab)
    scene.add_object(sametab)


scene.run_tasks()
