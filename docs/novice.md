# Novice Example - Exploring EVEN more functionality!

## Event Handlers
See [events.md](events.md)
```python
def mouse_handler(evt):
    print(evt.type)
    # do amazing stuff here

# pro tip: you can actually update an object directly in the arena update_object function
arena.update_object(cube, clickable=True, evt_handler=mouse_handler)
# arena.update_object(cube, click_listener=True, evt_handler=mouse_handler) # also works
```

## Deleting Attributes
```python
cube.update_attributes(click_listener=None)
# cube.update_attributes(click_listener=False) # also works
```

## Deleting Objects
```python
arena.delete_object(cube)
```

# Appendix
```python
from arena import *

# setup library
arena = Arena("arena.andrew.cmu.edu", "example", "realm")

@arena.run_async
async def func():
    # make a cube
    cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
    arena.add_object(cube)

    def mouse_handler(evt):
        if evt.type == "mousedown":
            cube.data.position.x += 0.5
            arena.update_object(cube)

    # add click_listener
    arena.update_object(cube, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

    # delete cube
    arena.delete_object(cube)

# start tasks
arena.start_tasks()
```
