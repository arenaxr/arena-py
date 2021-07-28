#!/usr/bin/env python
import time

from arena import *
import numpy as np

scene = Scene(host="arenaxr.org", scene="example")

DIMENSION = 10
OCCUPANT_NAME = "my_occupant"

last_loc = (0, 0, 0)

@scene.run_once
def make_store():
    my_json_store = JSON(
        object_id="occupancy_grid",
        json_data={
            "grid": np.full(
                (DIMENSION, DIMENSION, DIMENSION),
                {}
            ).tolist()
        }
    )
    scene.add_object(my_json_store)

@scene.run_forever(interval_ms=250)
def fill_grid():
    if "occupancy_grid" in scene.all_stores:
        global last_loc
        store = scene.all_stores["occupancy_grid"]
        i, j, k = last_loc
        updates = []
        updates.append(
            f'del(.grid[{i}][{j}][{k}].{OCCUPANT_NAME})'
        )
        last_loc = (i+1, j, k)
        if (i+1 > DIMENSION - 1):
            last_loc = (0, j, k)
        i, j, k = last_loc
        updates.append(
            f'.grid[{i}][{j}][{k}] += {{"{OCCUPANT_NAME}": {{}}}}'
        )
        print(updates)
        scene.update_store(store, jq_updates=updates)
scene.run_tasks()