from arena import *
import random


def user_leave_callback(scene, cam, msg):
    print("left:", cam.object_id)
    print("Private Objects:", scene.get_private_objects())

def report_click(scene, evt, msg):
    if evt.type == "mousedown":
        print(f"User {evt.object_id} clicked on {evt.data.target}")

def user_join_callback(scene, cam, msg):
    username = cam.object_id
    print("joined:", username)
    random_y = 0.5 + random.randrange(3)
    random_z = -1 - random.randrange(5)
    user_text = Text(
        object_id=f"text_{username}",
        value=f"Hello {username}!",
        align="center",
        font="mozillavr",
        # https://aframe.io/docs/1.4.0/components/text.html#stock-fonts
        position=(0, random_y, random_z),
        scale=(1.5, 1.5, 1.5),
        color=(100, 255, 255),
        private_userid=username,
    )
    user_box = Box(
        object_id=f"box_{username}",
        position=(0, 0.75 + random_y, random_z),
        scale=(0.5, 0.5, 0.5),
        color=(100, 255, 255),
        private_userid=username,
        clickable=True,
        evt_handler=report_click,
    )
    scene.add_object(user_text)
    scene.add_object(user_box)
    print("Private Objects:", scene.get_private_objects())

scene = Scene(host="arenaxr.org", scene="example")
scene.user_join_callback = user_join_callback
scene.user_left_callback = user_leave_callback

scene.run_tasks()