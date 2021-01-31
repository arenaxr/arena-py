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

@arena.run_forever(interval_ms=1000)
def periodic():
    global x
    global xr_logo    # non allocated variables need to be global

    if x%4==0:
        # Trigger a single "wave" animation
        arena.update_object(xr_logo, animation_mixer=Animation(clip="wave", loop="once" ) )
        print( "Wave Once")
    if x%4==1:
        arena.update_object(xr_logo, animation_mixer=Animation(clip="rotate",loop="once" ) )
        print( "Rotate Once")
    if x%4==2:
        # Test wildcard for multiple clips
        arena.update_object(xr_logo, animation_mixer=Animation(clip="*", loop="repeat" ) )
        print( "Wave and Rotate Repeat")
    if x%4==3:
        arena.update_object(xr_logo, animation_mixer=Animation(clip="*",loop="repeat" ) )
        arena.update_object(xr_logo, animation=Animation(property="position",start=(0,0,-5), end=(0,0,-10),easing="linear",dur=1000 ) )
        arena.update_object(xr_logo, animation__2=Animation(property="rotation",start=(0,0,0), end=(0,360,0),easing="linear",dur=1000 ) )
        print( "Wave and Rotate Repeat and move with tweening")

    x=x+1


arena.run_tasks()
