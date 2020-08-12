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
SCENE = "arm"

robot1Scale = 0.002
robot2Scale = 0.01

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

animateState = False

def arm_click_handler(event=None):
    global animateState
    print("ARM event handler")

    if event.event_type == arena.EventType.mousedown:
        draw_ray(event.click_pos, event.position)
        print("ARM click!")
        if animateState == False:
            animateStr = '{"animation-mixer": {"clip": "Armature.002|Armature.002Action.001"}}'
            arm1 = arena.Object(
                objName="arm1",
                url="models/factory_robot_arm/scene.gltf",
                objType=arena.Shape.gltf_model,
           #     scale=(0.001,0.001,0.001),
           #     location=(0,0,-4),
                rotation=(0.7,0,0,0.7),
                scale=(robot1Scale,robot1Scale,robot1Scale),
                location=(0,0,0),
                data=animateStr,
                clickable=True,
                callback=arm_click_handler
            )
            animateState = True
        else:
            animateStr = '{"animation-mixer": {"clip": "pause"}}'
            arm1 = arena.Object(
                objName="arm1",
                url="models/factory_robot_arm/scene.gltf",
                objType=arena.Shape.gltf_model,
           #     scale=(0.001,0.001,0.001),
           #     location=(0,0,-4),
                rotation=(0.7,0,0,0.7),
                scale=(robot1Scale,robot1Scale,robot1Scale),
                location=(0,0,0),
                data=animateStr,
                clickable=True,
                callback=arm_click_handler
            )
            animateState = False




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


#    arena.Object(
#     #   objType=arena.Shape.cube,
#        objType=shapeType,
#        persist=False,
#        objName="cube"+str(i),
#        physics=arena.Physics.dynamic,
#        collision_listener=True,
#        impulse=arena.Impulse("mouseup",( 5,30,0),(30,1,1)),
#        location=(random.randrange(-10,10), 0.5, random.randrange(-10,10)),
#        color=random_color(),
#        scale=(0.6, 0.6, 0.6),
#        clickable=True,
#        callback=guac_callback,
#    )
TAG = arena.Object(objName="apriltag_72",
                   transparency=arena.Transparency(True, 0),
                   persist=True)

arm1 = arena.Object(
                # location=(face.trans[0]/10, face.trans[1]/10+3, (face.trans[2]+50)/10-5),
                # rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
                objName="arm1",
                url="models/factory_robot_arm/scene.gltf",
                objType=arena.Shape.gltf_model,
                rotation=(0.7,0,0,0.7),
                scale=(robot1Scale,robot1Scale,robot1Scale),
                location=(0,0,0),
                # data=morphStr,
                clickable=True,
                parent=TAG.objName,
                callback=arm_click_handler
)

TAG2 = arena.Object(objName="apriltag_73",
                   transparency=arena.Transparency(True, 0),
                   persist=True)

arm1 = arena.Object(
                # location=(face.trans[0]/10, face.trans[1]/10+3, (face.trans[2]+50)/10-5),
                # rotation=(0,0,0.6-openness,1), # quaternion value roughly between -.05 and .05
                objName="arm2",
                url="models/industrial_robot_arm/scene.gltf",
                objType=arena.Shape.gltf_model,
                rotation=(0.7,0,0,0.7),
                scale=(robot2Scale,robot2Scale,robot2Scale),
                location=(0,0,0),
                # data=morphStr,
                clickable=True,
                parent=TAG2.objName,
                callback=arm_click_handler
)


#cube1.delete()


arena.handle_events()
