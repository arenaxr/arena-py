"""Videosphere

Create a large videosphere for displaying live 360 camera video using the Jitsi video stream.

To use a live Ricoh Theta or similar 360 camera:
1. Create this videosphere with a `jitsi_video` displayName (e.g. `my-360-cam`).
2. Connect the 360 camera as a video source in your browser.
3. In the ARENA scene, open A/V Setup and select the 360 camera as your video device.
4. Set your display name to match the `jitsi_video` displayName (e.g. `my-360-cam`).
5. Enable the camera in A/V Setup. The live feed will be mapped onto the videosphere interior.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_videosphere():
    my_videosphere = Videosphere(
        object_id="my_videosphere",
        position=(0, 0, 0),
        radius=150,
        jitsi_video=JitsiVideo(displayName="my-360-cam"),
        persist=True,
    )
    scene.add_object(my_videosphere)


scene.run_tasks()
