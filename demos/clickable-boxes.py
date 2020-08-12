# guac.py
#
# plays Tic Tac Toe
# clicked boxes alternate red and blue
# boxes fall if no winner
# boxes launch upon win
# avocado "Vanna White" reacts accordingly

import time
import arena
import random

HOST = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "tracer2"


def draw_ray(click_pos, position):
    line = arena.Object(
        #objName="line1",
        ttl=1,
        objType=arena.Shape.thickline,
        thickline=arena.Thickline( # slightly below camera so you can see line vs head-on
            {
                (click_pos[0],click_pos[1]-0.2,click_pos[2]),
                (position[0],position[1],position[2])
            },5,"#FF00FF")
    )


def guac_callback(event=None): # gets a GenericEvent
    # only mousedown messages
    if event.event_type == arena.EventType.mousedown:

        # draw a ray from clicker to cube
        draw_ray(event.click_pos, event.position)

def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)


# start the fun shall we?

arena.init(HOST, REALM, SCENE)
# make a parent scene object
print("starting main loop")

#    name = "cube_" + str(x) + "_" + str(y)

for i in range(100):

    arena.Object(
        objType=arena.Shape.cube,
        persist=False,
        objName="cube"+str(i),
        # messes up child-follow-parent pose
        physics=arena.Physics.dynamic,
        collision_listener=True,
        #transparency=arena.Transparency(True,0.5),
        impulse=arena.Impulse("mouseup",( 5,30,0),(30,1,1)),
        location=(random.randrange(-10,10), 1, random.randrange(-10,10)),
        color=random_color(),
        scale=(0.6, 0.6, 0.6),
        clickable=True,
        callback=guac_callback,
    )

#cube1.delete()


arena.handle_events()
