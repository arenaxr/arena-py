# Novice Example - Exploring EVEN more functionality!

## Event Handlers
See [events.md](events.md)
```python
def mouse_handler(scene, evt, msg):
    print(evt.type)
    # do amazing stuff here

# pro tip: you can actually update an object directly in the arena update_object function
arena.update_object(box, clickable=True, evt_handler=mouse_handler)
# arena.update_object(box, click_listener=True, evt_handler=mouse_handler) # also works
```

## Deleting Attributes
```python
box.update_attributes(click_listener=None)
# box.update_attributes(click_listener=False) # also works
```

## Deleting Objects
```python
arena.delete_object(box)
```

# Appendix
```python
from arena import *

# setup library
arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_async
async def func():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    arena.add_object(box)

    def mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            box.data.position.x += 0.5
            arena.update_object(box)

    # add click_listener
    arena.update_object(box, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

    # delete box
    arena.delete_object(box)

# start tasks
arena.run_tasks()
```
