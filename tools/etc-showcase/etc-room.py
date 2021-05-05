from arena import *
import time

scene = Scene(host="arenaxr.org",realm="realm",scene="etc-room")

rot_state=0
start_rot=0

# This sets up the screenshare.  It first created a decoy screenshare called "screenshare"
# that is tiny and far off so nobody can really use it.  It then creates a real screen
# called "etc-share" within the screenshare frame for the scene that the students can use.
@scene.run_once
def create_screenshare():
    screenshare_diversion = Box(
            object_id="screenshare",
            position=Position(0,-1000,0),
            scale=Scale(0,0,0),
            persist=True
        )
    scene.add_object(screenshare_diversion)
    print("Added Screenshare box")

    screenshare = Box(
            object_id="etc-share",
            color=Color(255,255,255),
            position=Position(52,8,23),
            rotation=Rotation(0,41.19,0),
            scale=Scale(16,10,0.1),
            clickable=True,
            persist=True
        )
    scene.add_object(screenshare)
    print("Added Screenshare box")


# This function grabs the Button object, makes it clickable and links it to an action that
# spings the TriBoard (also loaded here)
@scene.run_once
def get_sign():
    global sign 
    global loaded

    # Get the sign model from persist / check that it exists
    sign = scene.get_persisted_obj("TriBoard")
    if isinstance(sign,GLTF) == False:
        print("Sorry, could not load sign object!")
    else:
        print("Loaded:")
        print(sign)

    # Get a button and add the click_handler function
    button = scene.get_persisted_obj("[PushButton]")
    if isinstance(button,GLTF) == False:
        print("Sorry, could not load button object!")
    else:
        print("Loaded:")
        print(button)
        button.update_attributes(evt_handler=click_handler)
        button.update_attributes(clickable=True)
        scene.update_object(button)
    
# click_handler function that rotates sign when clicked
# if not the "PushButton" object, it draws a laser ray
def click_handler(scene,evt,msg):
    global sign # non allocated variables need to be global
    global rot_state

    print("Got Click Event from:" + evt.object_id)
    if evt.type == "mousedown":
        if evt.object_id=="[PushButton]":
            last_rot=rot_state        
            rot_state-=(360/3)%360
            # Set the baseline rotation before launching animation to avoid flicker
            sign.data.rotation.y=last_rot
            scene.update_object(sign)
            # Set that actual animation
            sign.dispatch_animation( Animation(property="rotation",start=(0,last_rot,0),end=(0,rot_state,0),easing="linear",dur=500 ) )
            scene.update_object(sign) # can also use update_object to run dispatched animations
            print( "Poster Switch")
        else:
            start = evt.data.clickPos
            end = evt.data.position
            start.y=start.y-.1
            start.x=start.x-.1
            start.z=start.z-.1
            line = ThickLine(path=(start,end), color=(255,0,0), lineWidth=5, ttl=1)
            scene.add_object(line)
            ball = Sphere( position=end, scale = (0.06,0.06,0.06), color=(255,0,0), ttl=1)
            scene.add_object(ball)
    

# Load all clickable objects for laser
# Note that objects made clickable while the program is running won't be added to this list
@scene.run_once
def load_all_clickables():
    objs = scene.get_persisted_objs()
    for obj_id,obj in objs.items():
        # obj.update_attributes(clickable=True)
        if obj.clickable:
            obj.update_attributes(evt_handler=click_handler)
            scene.update_object(obj)
            print(obj)

scene.run_tasks()
