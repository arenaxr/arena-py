"""Program Callbacks

`scene.end_program_callback` is called whenever the program is ending from the SIGINT, Crtl-C, or other kill process.
Use this to cleanup resources you don't want in the scene when the program ends.
This is especially useful for persisted objects use created that you want to be removed.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

childObject = Box(object_id="child_object")
appParentObject = Object(object_id="parent_object", parent=childObject.object_id)


# [scene] is the Scene that called the callback
def end_program_callback(scene):
    # do stuff with scene root objects here
    scene.delete_object(appParentObject)
    print("App Terminated.")
    # etc.


scene.end_program_callback = end_program_callback
