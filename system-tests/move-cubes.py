# move-cubes.py
#
# Make two boxes that move away from each other (and a bunch of dodecahedrons!).
# For testing tasks and object creation.

from arena import *
import random


scene = Scene(host="arenaxr.org", realm="realm", scene="test")


music_on = False
def evt_handler(scene, event, msg):
    global music_on

    print("clicked", music_on)
    music_on = not music_on
    if music_on:
        scene.update_object(box, sound=Sound(positional=True, poolSize=1, autoplay=True, src="store/users/wiselab/audio/september.mp3"))


box = Box(object_id="box", position=Position(0,3,0), scale=Scale(2,2,2), click_listener=True, evt_handler=evt_handler)
scene.add_object(box)

sphere = Sphere(object_id="sphere", position=Position(0,3,0), scale=Scale(1.5,1.5,1.5))
scene.add_object(sphere)


@scene.run_once(text="arena-py 0.1.0!", parent="sphere")
def make_text(text, parent):
    text_obj = Text(text=text, position=Position(0,1.5,0), parent=parent)
    scene.add_object(text_obj)
    print(sphere.object_id, text, parent)


i = 0
@scene.run_forever(interval_ms=500, arg="hi")
def move_box(arg):
    global i # non allocated variables need to be global
    box.update_attributes(position=Position(i,3,0))
    scene.update_object(box)
    i += 0.2
    print(arg)


j = 0
def move_sphere():
    global j # non allocated variables need to be global
    sphere.update_attributes(position=Position(j,3,0))
    scene.update_object(sphere)
    j -= 0.5


def make_dodecahedrons():
    scene.add_object(Dodecahedron(position=Position(random.randint(-10,10),random.randint(0,5),random.randint(-10,10))))


scene.run_once(make_text, text="arena-py 0.1.0?", parent="box")
scene.run_forever(move_sphere, 1000)
scene.run_forever(make_dodecahedrons, 2000)


scene.run_tasks() # will block
