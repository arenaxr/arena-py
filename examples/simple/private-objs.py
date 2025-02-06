from arena import *
import random


def user_leave_callback(scene, cam, msg):
    print("left:", cam.object_id)
    print("Private Objects:", scene.get_private_objects())

def user_join_callback(scene, cam, msg):
    username = cam.object_id
    print("joined:", username)
    user_text = Text(
        object_id=f"text_{username}",
        value=f"Hello {username}!",
        align="center",
        font="mozillavr",
        # https://aframe.io/docs/1.4.0/components/text.html#stock-fonts
        position=(0, 0.5 + random.randrange(3), -1 -random.randrange(5)),
        scale=(1.5, 1.5, 1.5),
        color=(100, 255, 255),
        private=True,
        private_userid=username
    )
    scene.add_object(user_text)
    print("Private Objects:", scene.get_private_objects())

scene = Scene(host="arenaxr.org", scene="example")
scene.user_join_callback = user_join_callback
scene.user_left_callback = user_leave_callback

scene.run_tasks()