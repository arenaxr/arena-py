# Events in ARENA-py

Events are ways to interact with user input in the ARENA.

## Events

### Get Event type
Can be one of either :  "mousedown", "mouseup", "mouseenter", "mouseleave"
```python
# evt = Event(...)
evt.type
```
## Get Event data

```python
# evt = Event(...)
evt.data.clickPos
evt.data.position
evt.data.source
```

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
