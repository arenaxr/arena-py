from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_dynamic_box():
    dynamic_box = Box(
        object_id="dynamic-box",
        depth=0.05,
        height=0.05,
        width=0.05,
        position=Position(0, 1,  0),
        material=Material(color="#0084ff", opacity=0.5, transparent=True),
        armarker=Armarker(
            markerid="1",
            markertype="apriltag_36h11",
            size=50,
            buildable=False,
            dynamic=True,
        )
    )
    scene.add_object(dynamic_box)


scene.run_tasks()
