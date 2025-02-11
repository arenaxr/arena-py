"""Goto URL

Creates three clickable URL boxes targeted to different windows.

Navigates to entirely new page into browser when clicked, or other event (requires `click-listener`).
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

goto_popup = GotoUrl(
    dest="popup",
    on="mousedown",
    url="https://www.conix.io/",
)
goto_newtab = GotoUrl(
    dest="newtab",
    on="mousedown",
    url="https://wise.ece.cmu.edu/",
)
goto_sametab = GotoUrl(
    dest="sametab",
    on="mousedown",
    url="https://www.ece.cmu.edu/",
)

popup = Box(
    position=(-3, 0, -5),
    color=(255, 0, 0),
    clickable=True,
    goto_url=goto_popup,
)

newtab = Box(
    position=(0, 0, -5),
    color=(0, 255, 0),
    clickable=True,
    goto_url=goto_newtab,
)

sametab = Box(
    position=(3, 0, -5),
    color=(0, 0, 255),
    clickable=True,
    goto_url=goto_sametab,
)


@scene.run_once
def make_urls():
    scene.add_object(popup)
    scene.add_object(newtab)
    scene.add_object(sametab)


scene.run_tasks()
