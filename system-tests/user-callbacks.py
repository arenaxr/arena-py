# user-callbacks.py
#
# Tests user callbacks

from arena import *

def user_join_callback(camera):
    print(f"User found: {camera.displayName} [object_id={camera.object_id}]")

def user_left_callback(camera):
    print(f"User left: {camera.displayName} [object_id={camera.object_id}]")

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="test")
scene.user_join_callback = user_join_callback
scene.user_left_callback = user_left_callback

scene.run_tasks()
