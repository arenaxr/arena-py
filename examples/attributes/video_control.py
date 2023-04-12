from arena import *

scene = Scene(host="arenaxr.org", scene="example")

video_control = VideoControl(
    frame_object="store/users/wiselab/images/conix-video-2.png",
    video_object="square_vid1",
    video_path="store/users/wiselab/videos/one-minute-madness-sm.mp4",
    anyone_clicks=True,
    video_loop=False
)


@scene.run_once
def make_music_box():
    my_box = Box(
        object_id="square_vid1",
        position=Position(
            x=19,
            y=1,
            z=-13.6
        ),
        material=Material(
            color="#808080",
            src="",
            side="front"
        ),
        scale=Scale(
            x=7,
            y=4.5,
            z=0.1
        ),
        video_control=video_control
    )

    scene.add_object(my_box)


scene.run_tasks()
