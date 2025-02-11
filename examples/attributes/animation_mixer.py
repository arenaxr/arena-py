"""Animating GLTF Models

To animate a GLTF model (see [GLTF Files](/content/3d-content/gltf-files) for how to find animation names), and set the animation-mixer parameter.

The `clip` asterisk means "play all animations", and works better in some situations, where other times the name of a specific animation in the GLTF file works (or maybe several in sequence).
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

animation_mixer_wave = AnimationMixer(
    clip="wave",
    loop="once",
)
animation_mixer_rotate = AnimationMixer(
    clip="rotate",
    loop="once",
)
animation_mixer_all = AnimationMixer(
    clip="*",
)

t = 0
xr_logo = GLTF(
    object_id="xr-logo",
    position=(0, 2, -5),
    scale=(1.0, 1.0, 1.0),
    url="store/users/wiselab/models/XR-logo.glb",
    persist=True,
)


@scene.run_forever(interval_ms=2000)
def wave_or_rotate():
    global t

    if t % 2 == 0:
        # Trigger a "wave" animation
        xr_logo.dispatch_animation(animation_mixer_wave)
        scene.run_animations(xr_logo)
        print("wave")
    else:
        xr_logo.dispatch_animation(animation_mixer_rotate)
        scene.run_animations(xr_logo)
        print("rotate")

    t += 1


scene.run_tasks()
