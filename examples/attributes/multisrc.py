from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_die1():
    die1 = Box(
        object_id="die1",
        position=Position(0, 3,  -2),
        material=Material(color="#ffffff"),
        multisrc=Multisrc(
            srcspath="store/users/wiselab/images/dice/",
            srcs="side1.png,side2.png,side3.png,side4.png,side5.png,side6.png"
        )
    )
    scene.add_object(die1)


scene.run_tasks()
