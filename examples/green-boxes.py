from arena import *
import random
import time
import sys

arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

color = (0, 255, 0)

# more complex case: Create many boxes

x = 1

@arena.run_forever(interval_ms=500)
def make_boxs():
    global x

    # Create a bunch of green boxes drawn directly to screen
    position = (random.randrange(10)-5,
                random.randrange(10),
                -random.randrange(10))
    box = Box(
            position=position,
            material=Material(color=color)
        )
    arena.add_object(box)
    x = x + 1

    print("object " + str(x-1) + " at " + str(position))

arena.run_tasks()
