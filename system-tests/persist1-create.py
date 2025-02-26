"""Persist 1, Create

Shows two programs interacting with the same object. Program 1 will create
a clickable object with random id and color. Program 2 will print the id and
color for the object when the object is clicked.

This simulates interacting with multiple clients, some may generate objects
persisting in the scene, which others may later need to interact with.
"""

from arena import *

# PROGRAM ONE - Create persisted object


program1 = Scene(host="arenaxr.org",
                 scene="persist-test")


@program1.run_once
def make_box():
    obj = Box(persist=True, clickable=True,
              color=(145, 195, 212))
    program1.add_object(obj)
    print(f"Program 1 persisted object: {obj.object_id}")
    print(f"Program 1 persisted color: {obj.data.color}")


program1.run_tasks()
