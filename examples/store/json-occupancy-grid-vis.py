#!/usr/bin/env python
from arena import *

scene = Scene(host="arenaxr.org", scene="example")

boxes = []
GRID_CUBE_SIZE = 5

@scene.run_forever(interval_ms=100)
def vis_grid():
    if "occupancy_grid" in Store.all_stores:
        grid = Store.all_stores["occupancy_grid"].data.json_data["grid"]

        if len(boxes) == 0:
            print("creating grid")
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    for k in range(len(grid[i][j])):
                        if len(grid[i][j][k]) == 0:
                            color = (0,255,0)
                            opacity = 0.1
                        else:
                            color = (255,0,0)
                            opacity = 0.5
                        boxes.append(Box(
                            object_id=f"occ-vis-{i}-{j}-{k}",
                            position=(i*GRID_CUBE_SIZE,j*GRID_CUBE_SIZE,k*GRID_CUBE_SIZE),
                            scale=(GRID_CUBE_SIZE,GRID_CUBE_SIZE,GRID_CUBE_SIZE),
                            color=color,
                            material=Material(opacity=opacity)
                        ))
            for box in boxes:
                scene.add_object(box)
        else:
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    for k in range(len(grid[i][j])):
                        if len(grid[i][j][k]) == 0:
                            color = (0,255,0)
                            opacity = 0.1
                        else:
                            color = (255,0,0)
                            opacity = 0.5
                        box = Object.all_objects[f"occ-vis-{i}-{j}-{k}"]
                        if (box.data.color["green"] != color[1] or
                            box.data.color["red"] != color[0]):
                            box.update_attributes(
                                color=color,
                                material=Material(opacity=opacity))
                            scene.update_object(box)

scene.run_tasks()
