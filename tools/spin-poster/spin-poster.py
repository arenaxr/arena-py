from arena import *

scene = Scene(host="arenaxr.org",scene="spin-poster")

rot=0
start_rot=0
sign_x=0
sign_y=0
sign_z=-10

@scene.run_once
def make_sign():
    global sign
    global button
    sign = GLTF(
        object_id="sign",
        position=(sign_x,sign_y,sign_z),
        rotation=(0,start_rot,0),
        scale=(1.0,1.0,1.0),
        url="https://www.dropbox.com/s/t79g0anj25dzjcc/sign.glb?dl=0",
        persist=True
    )
    scene.add_object(sign)

    # Not a child so it doesn't rotate
    button = GLTF(
        object_id="button",
        position=(sign_x,sign_y,sign_z+1),
        scale=(1.0,1.0,1.0),
        rotation=(0,start_rot+90,0),
        url="https://www.dropbox.com/s/2wkqc19i3ulhbqz/button.glb?dl=0",
        persist=True,
        clickable=True,
        evt_handler=click_handler
    )
    scene.add_object(button)

    slide1_material = Material(src="https://www.dropbox.com/s/3hccefrz6ywlknh/slide1.png?dl=0")
    slide1 = Box(
        object_id="slide1",
        position=Position(0,3.21,0.57),
        rotation=(0,0,0),
        scale={"x":1.85,"y":3.35,"z":0},
        material=slide1_material,
        persist=True,
        parent="sign"
    )
    scene.add_object(slide1)


    slide2_material = Material(src="https://www.dropbox.com/s/xvh920h7zqeqaqd/slide2.png?dl=0")
    slide2 = Box(
        object_id="slide2",
        position=Position(0.47,3.21,-.30),
        rotation=(0,120,0),
        scale={"x":1.85,"y":3.35,"z":0},
        material=slide2_material,
        persist=True,
        parent="sign"
    )
    scene.add_object(slide2)

    slide3_material = Material(src="https://www.dropbox.com/s/krxk5n4kxetaxcd/slide3.png?dl=0")
    slide3 = Box( object_id="slide3",
        position=Position(-0.50,3.21,-.30),
        rotation=(0,-120,0),
        scale={"x":1.85,"y":3.35,"z":0},
        material=slide3_material,
        persist=True,
        parent="sign"
    )
    scene.add_object(slide3)

    print("Poster Loaded")


def click_handler(scene,evt,msg):
    global rot
    global sign # non allocated variables need to be global

    if evt.type == "mousedown":
        last_rot=rot
        rot-=(360/3)%360
        # Set the baseline rotation before launching animation to avoid flicker
        sign.data.rotation.y=last_rot
        scene.update_object(sign)
        # Set that actual animation
        sign.dispatch_animation( Animation(property="rotation",start=(0,last_rot,0),end=(0,rot,0),easing="linear",dur=500 ) )
        scene.update_object(sign) # can also use update_object to run dispatched animations
        print( "Poster Switch")



scene.run_tasks()
