from arena import *

scene = Scene(host="arenaxr.org", scene="example")

sound = Sound(positional=True, poolSize=1, autoplay=True, src="store/users/wiselab/audio/september.mp3")

@scene.run_once
def make_music_box():
    my_box = Box(
        object_id="my_box",
        sound=sound
    )

    scene.add_object(my_box)

scene.run_tasks()
