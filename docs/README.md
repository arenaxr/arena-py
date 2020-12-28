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

# setup library
arena = Arena("arena.andrew.cmu.edu", "realm", "example")

def main():
    # make a cube
    cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
    # add the cube
    arena.add_object(cube)

# add and start tasks
arena.run_once(main)
arena.run_tasks()
```
