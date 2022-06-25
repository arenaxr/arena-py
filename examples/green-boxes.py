from arena import *
import random
import time
import sys

scene = Scene(host="mqtt.arenaxr.org", auth_host="arenaxr.org", scene="example")

color = (0, 255, 0)

# more complex case: Create many boxes

x = 1

@scene.run_forever(interval_ms=500)
def make_boxs():
    global x

    # Create a bunch of green boxes drawn directly to screen
    position = (random.randrange(10)-5,
                random.randrange(10),
                -random.randrange(10))
    box = Box(
            position=position,
            color=color
        )
    scene.add_object(box)
    x = x + 1

    print("object " + str(x-1) + " at " + str(position))

scene.run_tasks()
