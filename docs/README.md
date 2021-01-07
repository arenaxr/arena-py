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

## A simple program

```python
from arena import *

# create library
arena = Arena("arena.andrew.cmu.edu", "realm", "example")

@arena.run_once # make this function a task that runs once at startup
def main():
    # make a cube
    cube = Cube(object_id="myCube", position=(0,3,-3), scale=(2,2,2))

    # add the cube to ARENA
    arena.add_object(cube)

# start tasks
arena.run_tasks()
```
