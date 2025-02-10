"""Events

Add the "click-listener" event to a scene object; click-listener is a Component defined in `events.js`. This works for adding other, arbitrary Components. A non-empty message gets sent to the Component's `init: ` function.

{
  "object_id": "box_1",
  "action": "update",
  "type": "object",
  "data": { "click-listener": "enable" }
}
"""
