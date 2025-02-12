"""Hand

Hand is the (left or right) hand metadata pose and controller type of the user avatar.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


def hand_found_callback(scene, hand, msg):
    print("Controller Found:", hand.object_id, "| User:", hand.camera.object_id)


def hand_remove_callback(scene, hand, msg):
    print("Controller Removed:", hand.object_id, "| User:", hand.camera.object_id)


def user_join_callback(scene, user, msg):
    print("User Joined:", user.object_id)
    user.hand_found_callback = hand_found_callback
    user.hand_remove_callback = hand_remove_callback


scene.user_join_callback = user_join_callback

scene.run_tasks()
