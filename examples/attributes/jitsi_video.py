"""Video Stream

Example to stream video from Jitsi onto a geometry. Change the user display name to `my-name`, reload the scene page, and click the camera on button.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

jitsi_video = JitsiVideo(
    displayName="my-name",
)


@scene.run_once
def make_video_stream():
    video_stream = Box(
        object_id="video_stream",
        position=Position(0, 1, -3),
        persist=True,
        jitsi_video=jitsi_video,
    )
    scene.add_object(video_stream)


scene.run_tasks()
