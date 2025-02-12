"""Lines

Draw a purple line from (2, 2, 2) to (3, 3, 3).

{
  "object_id": "line_1",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "line",
    "start": { "x": 2, "y": 2, "z": 2 },
    "end": { "x": 3, "y": 3, "z": 3 },
    "color": "#CE00FF"
  }
}

Extend the line with a new segment, colored green.

{
  "object_id": "line_1",
  "action": "update",
  "type": "object",
  "data": {
    "line__2": {
      "start": { "x": 3, "y": 3, "z": 3 },
      "end": { "x": 4, "y": 4, "z": 4 },
      "color": "#00FF00"
    }
  }
}
A light.

More properties at <a href='https://aframe.io/docs/1.5.0/components/light.html'>A-Frame Light</a>.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

start = (0, 0, -3)
end = (5, 5, 5)


@scene.run_once
def make_line():
    line = Line(
        object_id="my_line",
        start=start,
        end=end,
        color=(0, 255, 0),
    )
    scene.add_object(line)


scene.run_tasks()
