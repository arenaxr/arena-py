"""Thicklines

A "thickline" (to improve openpose skeleton rendering visibility) - works like a line, but the `lineWidth` value specifies thickness, and multiple points can be specified at once, e.g. draw a pink line 11 pixels thick from 0, 0, 0 to 1, 0, 0 to 1, 1, 0 to 1, 1, 1. The shorthand syntax for coordinates is a bonus feature of lower level code; extending it for the rest of ARENA commands remains as an enhancement.

{
  "object_id": "thickline_8",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "thickline",
    "lineWidth": 11,
    "color": "#FF88EE",
    "path": "0 0 0, 1 0 0, 1 1 0, 1 1 1"
  }
}

You might be wondering, why can't normal lines just use the scale value to specify thickness? But this one goes to eleven! Really though, normal lines perform faster. To update a "thickline" takes a special syntax because thicklines are really "meshline"s.

{
  "object_id": "thickline_8",
  "action": "update",
  "type": "object",
  "data": {
    "meshline": {
      "lineWidth": 11,
      "color": "#ffffff",
      "path": "0 0 0, 0 0 1"
    }
  }
}
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

start = (0,0,-3)
end = (10,10,-10)

@scene.run_once
def make_thickline():
    thickline = ThickLine(
        object_id="my_thickline",
        lineWidth=20,
        path=(start, end),
        color=(0,255,0)
    )
    scene.add_object(thickline)

scene.run_tasks()
