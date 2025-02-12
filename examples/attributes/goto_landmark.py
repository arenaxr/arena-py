"""Goto Landmark

Teleports user to the landmark with the given name. Requires click-listener.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

landmark_sky_object_id = "landmark_sky"
landmark_teleport_object_id = "landmark_teleport"
goto_landmark = GotoLandmark(
    landmark=landmark_sky_object_id,
    on="mousedown",
)


@scene.run_once
def make_landmark_teleport():
    landmark_sky = Object(
        object_id=landmark_sky_object_id,
        position=Position(0, 100, 0),
        landmark=Landmark(label="Sky High Location"),
    )
    scene.add_object(landmark_sky)

    landmark_teleport = Box(
        object_id=landmark_teleport_object_id,
        position=Position(0, 1, -3),
        material=Material(color="#0084ff", opacity=0.5, transparent=True),
        clickable=True,
        goto_landmark=goto_landmark,
    )
    scene.add_object(landmark_teleport)


scene.run_tasks()
