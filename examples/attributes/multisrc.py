"""Images on Objects

Multi Source

Define multiple visual sources applied to an object.

Use the `multisrc` A-Frame Component to specify different bitmaps for sides of a box or other primitive shape.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

multisrc = Multisrc(
    srcspath="store/users/wiselab/images/dice/",
    srcs="side1.png,side2.png,side3.png,side4.png,side5.png,side6.png",
)


@scene.run_once
def make_die1():
    die1 = Box(
        object_id="die1",
        position=Position(0, 3, -2),
        material=Material(color="#ffffff"),
        multisrc=multisrc,
    )
    scene.add_object(die1)


scene.run_tasks()
