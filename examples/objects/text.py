"""Text

Add some red text that says "Hello World".

{
  "object_id": "text_3",
  "action": "create",
  "type": "object",
  "data": {
    "color": "red",
    "value": "Hello world!",
    "object_type": "text",
    "position": { "x": 0, "y": 3, "z": -4 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 1, "y": 1, "z": 1 }
  }
}

Change text color properties [A-Frame Text](https://aframe.io/docs/1.5.0/components/text.html#properties).

{
  "object_id": "text_3",
  "action": "update",
  "type": "object",
  "data": { "text": { "color": "green" } }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_once
def make_text():
    my_text = Text(
        object_id="my_text",
        value="Hello World!",
        align="center",
        font="mozillavr", # https://aframe.io/docs/1.4.0/components/text.html#stock-fonts
        position=(0,2,-3),
        scale=(1.5,1.5,1.5),
        color=(100,255,255),
    )
    scene.add_object(my_text)

scene.run_tasks()
