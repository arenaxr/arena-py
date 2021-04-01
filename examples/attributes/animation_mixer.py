from arena import *

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

xr_logo = GLTF(
    object_id="xr-logo",
    position=(0,2,-5),
    scale=(1.0,1.0,1.0),
    url="store/users/wiselab/models/XR-logo.glb",
    persist=True
)

t = 0

@scene.run_forever(interval_ms=2000)
def wave_or_rotate():
    global t

    if t % 2 == 0:
        # Trigger a "wave" animation
        xr_logo.dispatch_animation(
                AnimationMixer(clip="wave",loop="once" )
            )
        scene.run_animations(xr_logo)
        print("wave")
    else:
        xr_logo.dispatch_animation(
                AnimationMixer(clip="rotate",loop="once" )
            )
        scene.run_animations(xr_logo)
        print("rotate")

    t += 1

scene.run_tasks()
