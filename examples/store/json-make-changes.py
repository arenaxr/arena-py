#!/usr/bin/env python
import time

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_store():
    my_json_store = JSON(
        object_id="my_json_store",
        json_data={
            "times": []
        }
    )
    scene.add_object(my_json_store)

@scene.run_forever(interval_ms=2000)
def add_to_store():
    if "my_json_store" in scene.all_stores:
        store = scene.all_stores["my_json_store"]
        scene.update_store(store, jq_updates=[
            f'.times += [{time.time()}]'
        ])

scene.run_tasks()