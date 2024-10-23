# persist1-create.py
# persist2-discover.py
#
# Shows two programs interacting with the same object. Program 1 will create
# a clickable object with random id and color. Program 2 will print the id and
# color for the object when the object is clicked.
#
# This simulates interacting with multiple clients, some may generate objects
# persisting in the scene, which others may later need to interact with.

from arena import *

# PROGRAM TWO - Receive click and attributes


def on_msg_callback(scene, obj, _msg):
    if isinstance(obj, Event) and obj.type == "mousedown":
        print(f"Program 2 mousedown event: {obj.object_id}")
        obj = scene.get_persisted_obj(obj.object_id)
        print(f"Program 2 persisted color: {obj.data.color}")


program2 = Scene(
    host="arenaxr.org", scene="persist-test",
    on_msg_callback=on_msg_callback,
)

program2.run_tasks()
