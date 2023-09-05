from arena import *

scene = Scene(host="arenaxr.org", scene="example")

def hand_found_callback(scene, hand, msg):
    print("Controller Found:", hand.object_id, "| User:", hand.camera.object_id)

def user_join_callback(scene, user, msg):
    print("User Joined:", user.object_id)
    user.hand_found_callback = hand_found_callback

scene.user_join_callback = user_join_callback

scene.run_tasks()
