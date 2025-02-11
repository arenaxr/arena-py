"""Landmark

Creates a landmark that can be teleported to from the UI list, or is one of the random starting positions for the scene
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

landmark = Landmark(
    label="Box 1",
    randomRadiusMin=1,
    randomRadiusMax=2,
    lookAtLandmark=True,
)


@scene.run_once
def make_box():
    scene.add_object(
        Box(
            object_id="box_1",
            position=(1, 1, -1),
            landmark=landmark,
        )
    )


scene.run_tasks()
