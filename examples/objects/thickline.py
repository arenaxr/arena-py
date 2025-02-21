"""Thickline

Draw a line that can have a custom width.

A "thickline" (to improve openpose skeleton rendering visibility) - works like a line, but the `lineWidth` value specifies thickness, and multiple points can be specified at once, e.g. draw a pink line 11 pixels thick from 0, 0, 0 to 1, 0, 0 to 1, 1, 0 to 1, 1, 1. The shorthand syntax for coordinates is a bonus feature of lower level code; extending it for the rest of ARENA commands remains as an enhancement.

You might be wondering, why can't normal lines just use the scale value to specify thickness? But this one goes to eleven! Really though, normal lines perform faster. To update a `thickline` takes a special syntax because thicklines are really `meshline`s.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_thick_line():
    thickline = Thickline(
        object_id="thickline_8",
        lineWidth=11,
        path=((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)),
        color="#FF88EE",
    )
    scene.add_object(thickline)
    scene.update_object(
        thickline,
        meshline={
            "lineWidth": 11,
            "color": "#ffffff",
            "path": "0 0 0, 0 0 1",
        },
    )


scene.run_tasks()
