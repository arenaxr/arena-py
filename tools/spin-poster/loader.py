from arena import *

scene = Scene(host="arenaxr.org",realm="realm",scene="spin-poster")

rot=0
start_rot=0
sign_x=0
sign_y=0
sign_z=-10

@scene.run_once
def make_sign():

    # Load a model with specific object_id that you will use for addressing later
    # The url specifies the GLTF model
    sign = GLTF(
        object_id="my_sign_1",
        position=(sign_x,sign_y,sign_z),
        rotation=(0,start_rot,0),
        scale=(1.0,1.0,1.0),
        url="https://www.dropbox.com/s/t79g0anj25dzjcc/sign.glb?dl=0",
        persist=True
    )
    scene.add_object(sign)

    # Load a model with specific object_id that you will use for addressing later
    button = GLTF(
        object_id="my_button_1",
        position=(sign_x,sign_y,sign_z+1),
        scale=(1.0,1.0,1.0),
        rotation=(0,start_rot+90,0),
        url="https://www.dropbox.com/s/2wkqc19i3ulhbqz/button.glb?dl=0",
        persist=True,
    )
    scene.add_object(button)

    print("Poster Assets Loaded")


scene.run_tasks()
