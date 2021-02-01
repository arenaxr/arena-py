from arena import *

arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

x=0

@arena.run_once
def make_xr_logo():
    global xr_logo
    xr_logo = GLTF(
        object_id="xr-logo",
        position=(0, 0, -5),
        scale=(1.0, 1.0, 1.0),
        url="store/users/wiselab/models/XR-logo.glb",
        persist=True
    )
    arena.add_object(xr_logo)

close_eye = {
    "gltf-morph__0": {
        "morphtarget": "eyeTop",
        "value": "0.8"
    },
    "gltf-morph__1": {
        "morphtarget": "eyeBottom",
        "value": "0.8"
    }
}

open_eye = {
    "gltf-morph__0": {
        "morphtarget": "eyeTop",
        "value": "0.0"
    },
    "gltf-morph__1": {
        "morphtarget": "eyeBottom",
        "value": "0.0"
    }
}



@arena.run_forever(interval_ms=2500)
def periodic():
    global x
    global xr_logo    # non allocated variables need to be global

    if x%7==0:
        # Trigger a single "wave" animation
        xr_logo.dispatch_animation(
                AnimationMixer(clip="wave", loop="once" )
            )
        arena.run_animations(xr_logo)
        print( "Wave Once")
    if x%7==1:
        xr_logo.dispatch_animation(
                AnimationMixer(clip="rotate",loop="once" )
            )
        arena.run_animations(xr_logo)
        print( "Rotate Once")
    if x%7==2:
        # Test wildcard for multiple clips
        xr_logo.dispatch_animation(
                AnimationMixer(clip="*", loop="repeat" )
            )
        arena.run_animations(xr_logo)
        print( "Wave and Rotate Repeat")
    if x%7==3:
        # can input a list/tuple of animations
        xr_logo.dispatch_animation(
                (
                    AnimationMixer(clip="*",loop="repeat" ),
                    Animation(property="position", start=(0,0,-5), end=(0,0,-10),easing="linear",dur=1000 )
                )
            )
        xr_logo.dispatch_animation(
                Animation(property="rotation", start=(0,0,0), end=(0,180,0),easing="linear",dur=1000 )
            )
        arena.run_animations(xr_logo)
        print( "Wave and Rotate Repeat and move with tweening")
    if x%7==4:
        # Move object back to start (capturing previous location from animation)
        # When using animated positions, don't mix with standard Position( ) object
        xr_logo.dispatch_animation(
                AnimationMixer(clip="*",loop="once" )
            )
        xr_logo.dispatch_animation(
                Animation(property="position", start=(0,0,-10), end=(0,0,-5),easing="linear",dur=0 )
            )
        arena.run_animations(xr_logo)
    if x%7==5:
        arena.update_object(xr_logo, **close_eye )
        print( "Morph Target Close Eye")
    if x%7==6:
        arena.update_object(xr_logo, **open_eye )
        print( "Morph Target Open Eye")

    x=x+1


arena.run_tasks()
