# ARENA-py Documentation and Tutorials

## Tutorials
[Part 1](beginner.md)

[Part 2](intermediate.md)

[Part 3](novice.md)

[Part 4](advanced.md)

Code for these can be found [here](../examples/tutorial)

## General Documentation
[Attributes](attributes.md)

[Objects](objects.md)

[Events](events.md)

[Callbacks](callbacks.md)

[Tasks](tasks.md)

[Animations](animations.md)

## A simple program

```python
from arena import *

# create library
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_once # make this function a task that runs once at startup
def main():
    # make a box
    box = Box(object_id="myBox", position=(0,3,-3), scale=(2,2,2))

    # add the box to ARENA
    arena.add_object(box)

# start tasks
arena.run_tasks()
```
