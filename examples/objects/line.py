"""Lines

Draw a purple line from (2, 2, 2) to (3, 3, 3).

Extend the line with a new segment, colored green.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_simple_line():
    line = Line(
        object_id="line_1",
        start=(2, 2, 2),
        end=(3, 3, 3),
        color="#CE00FF",
    )
    scene.add_object(line)
    scene.update_object(
        line,
        line__2={
            "start": {"x": 3, "y": 3, "z": 3},
            "end": {"x": 4, "y": 4, "z": 4},
            "color": "#00FF00",
        },
    )


scene.run_tasks()
