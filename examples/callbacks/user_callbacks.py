"""User Callbacks

`scene.user_join_callback` is called whenever the library detects/finds a new user that it hasn't seen before in a scene.
Note: this is not necessarily called when a user "joins" a scene, rather, it is called when the library first sees a `Camera` object/receives an "update" message from a user.

`scene.user_left_callback` is called whenever a user leaves a scene/sends a delete message.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


def user_join_callback(scene, camera, msg):
    print(f"User found: {camera.displayName} [object_id={camera.object_id}]")
    ##Get access to user state
    # camera is a Camera class instance (see Objects)
    # etc.


def user_left_callback(scene, camera, msg):
    print(f"User left: {camera.displayName} [object_id={camera.object_id}]")
    # Get access to user state
    # camera is a Camera class instance (see Objects)
    # etc.


scene.user_join_callback = user_join_callback
scene.user_left_callback = user_left_callback
