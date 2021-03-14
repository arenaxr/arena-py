# ARENA-py Documentation and Tutorials

## Tutorials
[Part 1](beginner.md)

[Part 2](intermediate.md)

[Part 3](novice.md)

[Part 4](advanced.md)

Code for these can be found [here](../examples/tutorial)

## General Documentation
See [ARENA Documentation: Python](https://conix-center.github.io/ARENA/content/python/).

## A simple program
```python
from arena import *

# create library
scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@scene.run_once # make this function a task that runs once at startup
def main():
    # make a box
    box = Box(object_id="myBox", position=(0,3,-3), scale=(2,2,2))

    # add the box to ARENA
    scene.add_object(box)

# start tasks
scene.run_tasks()
```
