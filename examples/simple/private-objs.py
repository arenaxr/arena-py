"""Private Objects

This example demonstrates how to create private objects that only one user can see
by leveraging the private_userid attribute of an object and the underlying private
mqtt messaging topic mechanism.

Note that the `program_id` top level message attribute is automatically set for private
objects such that interactions by users on those private objects are directed back
to this program via private mqtt topics as well.

We also print the global private objects dict to show how it is cleaned up when
a user leaves the scene.
"""

import random

from arena import *


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
    # Text that only user can see
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
    # Clickable box that only user can see
    user_box = Box(
        object_id=f"box_{username}",
        position=(0, 0.75 + random_y, random_z),
        scale=(0.5, 0.5, 0.5),
        color=(100, 255, 255),
        private_userid=username,
        clickable=True,
        evt_handler=report_click,
    )
    # Red box that everyone can see
    user_public_box = Box(
        object_id=f"box_{username}_public",
        position=(0, 1.25 + random_y, random_z),
        scale=(0.5, 0.5, 0.5),
        color=(255, 0, 0),
    )
    scene.add_objects([user_text, user_box, user_public_box])
    print("Private Objects:", scene.get_private_objects())

scene = Scene(host="arenaxr.org", scene="example")
scene.user_join_callback = user_join_callback
scene.user_left_callback = user_leave_callback

scene.run_tasks()
