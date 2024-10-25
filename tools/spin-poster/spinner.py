import time

from arena import *

scene = Scene(host="arenaxr.org",scene="spin-poster")

rot_state=0
start_rot=0

@scene.run_once
def get_sign():
    global sign # non allocated variables need to be global
    global loaded

    # Get the sign model from persist / check that it exists
    sign = scene.get_persisted_obj("my_sign_1")
    if isinstance(sign,GLTF) == False:
        print("Sorry, could not load sign object!")
    else:
        print("Loaded:")
        print(sign)

    # Get a button and add the click_handler function
    button = scene.get_persisted_obj("my_button_1")
    if isinstance(button,GLTF) == False:
        print("Sorry, could not load button object!")
    else:
        print("Loaded:")
        print(button)
        button.update_attributes(evt_handler=click_handler)
        button.update_attributes(clickable=True)
        scene.update_object(button)

# click_handler function that rotates sign when clicked
def click_handler(scene,evt,msg):
    global sign # non allocated variables need to be global
    global rot_state

    print("Got Click Event from:" + evt.data.target)
    if evt.type == "mousedown":
        last_rot=rot_state
        rot_state-=(360/3)%360
        # Set the baseline rotation before launching animation to avoid flicker
        sign.data.rotation.y=last_rot
        scene.update_object(sign)
        # Set that actual animation
        sign.dispatch_animation( Animation(property="rotation",start=(0,last_rot,0),end=(0,rot_state,0),easing="linear",dur=500 ) )
        scene.update_object(sign) # can also use update_object to run dispatched animations
        print( "Poster Switch")



scene.run_tasks()
