from arena import *

scene = Scene(host="arenaxr.org",scene="example")

x=0

@scene.run_once
def make_xr_logo():
    global xr_logo
    xr_logo = GLTF(
        object_id="xr-logo",
        position=(0,0,-5),
        scale=(1.0,1.0,1.0),
        url="store/users/wiselab/models/XR-logo.glb",
        persist=True
    )
    scene.add_object(xr_logo)


@scene.run_forever(interval_ms=2500)
def periodic():
    global x
    global xr_logo    # non allocated variables need to be global

    if x%7==0:
        # Trigger a single "wave" animation
        xr_logo.dispatch_animation(
                AnimationMixer(clip="wave",loop="once" )
            )
        scene.run_animations(xr_logo)
        print( "Wave Once")

    if x%7==1:
        xr_logo.dispatch_animation(
                AnimationMixer(clip="rotate",loop="once" )
            )
        scene.run_animations(xr_logo)
        print( "Rotate Once")

    if x%7==2:
        # Test wildcard for multiple clips
        xr_logo.dispatch_animation(
                AnimationMixer(clip="*",loop="repeat" )
            )
        scene.run_animations(xr_logo)
        print( "Wave and Rotate Repeat")

    if x%7==3:
        # can input a list/tuple of animations
        xr_logo.dispatch_animation(
                [
                    AnimationMixer(clip="*",loop="repeat" ),
                    Animation(property="position",start=(0,0,-5),end=(0,0,-10),easing="linear",dur=1000 )
                ]
            )
        xr_logo.dispatch_animation(
                Animation(property="rotation",start=(0,0,0),end=(0,360,0),easing="linear",dur=1000 )
            )
        scene.update_object(xr_logo) # can also use update_object to run dispatched animations
        print( "Wave and Rotate Repeat and move with tweening")

    if x%7==4:
        # Move object back to start (capturing previous location from animation)
        # When using animated positions, don't mix with standard Position( ) object
        xr_logo.dispatch_animation(
                AnimationMixer(clip="*",loop="once" )
            )
        xr_logo.dispatch_animation(
                Animation(property="position",start=(0,0,-10),end=(0,0,-5),easing="linear",dur=1000 )
            )
        xr_logo.dispatch_animation(
                Animation(property="rotation",start=(0,360,0),end=(0,0,0),easing="linear",dur=1000 )
            )
        scene.run_animations(xr_logo)

    if x%7==5:
        close_eye_morphs = [Morph(morphtarget="eyeBottom",value=0.8), Morph(morphtarget="eyeTop",value=0.8)]
        xr_logo.update_morph(close_eye_morphs)
        scene.update_object(xr_logo)
        print( "Morph Target Close Eye")

    if x%7==6:
        open_eye_morphs = [Morph(morphtarget="eyeTop",value=0.0), Morph(morphtarget="eyeBottom",value=0.0)]
        xr_logo.update_morph(open_eye_morphs)
        scene.update_object(xr_logo)
        print( "Morph Target Open Eye")

    x=x+1


scene.run_tasks()
