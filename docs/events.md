# Events in ARENA-py

Events are ways to interact with user input in the ARENA.

See https://arena.conix.io/content/messaging/examples.html.

## Click Events
There are several types of click events that you can generate ("mousedown", "mouseup", "mouseenter", "mouseleave", "triggerdown", "triggerup"):
```python
arena.generate_click_event(obj, type, ...)

# add a click listener to an object to be able to click it
obj.update_attributes(clickable=True)
# generate a "fake" click event from ARENA-py
arena.generate_click_event(
    obj,
    type="mouseup"
)
# ARENA-py will "click" obj with mouseup. In JSON, "source" will be defined as "arena_lib_[some random id here]".
```

## Camera Manipulation Events
You can also move a user's camera and/or make it look at a specific location of object:
```python
arena.manipulate_camera(obj, type, ...)

# move camera:
arena.manipulate_camera(
    camera,
    type="camera-override",
    position=(rando(),1.6,rando()),
    rotation=(0,0,0,1)
)

# make camera look at something/some position:
arena.manipulate_camera(
    camera,
    type="look-at",
    target=cube # can also do a position: (0,0,0)
)
```

## Generic Events
If there is an event that does not exist yet, you can use this to have more freedom in the event type.
```python
# define custom event
evt = Event(type="my_custom_event", position=(3,4,5), target=sphere)
# generate custom event with ARENA-py client
arena.generate_custom_event(evt, action="clientEvent")
```

# Event Parameters and Data
When you attach an ```evt_handler``` to an Object, you will receive Event objects in your handler. Below are how you access attributes of the Event object.

```python
def click_handler(evt): # evt = Event(...)
    print(evt)

    ## Get Event type
    evt.type # == "mousedown", "mouseup", "mouseenter", "mouseleave", "triggerdown", or "triggerup"

    ## Get Event data
    evt.data.clickPos
    evt.data.position
    evt.data.source
    # etc etc

cube = Cube(..., evt_handler=click_handler)
```

# Appendix
```python
Event(object_id, action, type, ...)
```

<!-- # Generating events with ARENA-py
You can generate click and camera events with ARENA-py like so:
```python
arena.generate_event(my_camera, type="camera-override")
``` -->

# ARENA Event JSON example
```json
{
    "object_id": "my_cube",
    "action": "clientEvent",
    "type": "mousedown",
    "data": {
        "clickPos": {
            "x": -1.525,
            "y": 1.6,
            "z": 12.171
        },
        "position": {
            "x": 0.318,
            "y": 4.02,
            "z": -1
        },
        "source": "[source goes here here]"
    },
    "timestamp": "[time goes here]"
}
```
