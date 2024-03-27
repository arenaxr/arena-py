from .animation import Animation

class AnimationMixer(Animation):
    """
    AnimationMixer attribute class to manage its properties in the ARENA: A list of available animations can usually be found by inspecting the model file or its documentation. All animations will play by default. To play only a specific set of animations, use wildcards: animation-mixer='clip: run_*'. More properties at <https://github.com/n5ro/aframe-extras/tree/master/src/loaders#animation> A-Frame Extras Animation.
    Usage: `animation_mixer=AnimationMixer(...)`

    :param bool clampWhenFinished: If true, halts the animation at the last frame. (optional)
    :param str clip: Name of the animation clip(s) to play. Accepts wildcards. Defaults to '*' (optional)
    :param float crossFadeDuration: Duration of cross-fades between clips, in seconds. (optional)
    :param float duration: Duration of the animation, in seconds (0 = auto). (optional)
    :param str loop: In repeat and pingpong modes, the clip plays once plus the specified number of repetitions. For pingpong, every second clip plays in reverse. Allows [once, repeat, pingpong] Defaults to 'repeat' (optional)
    :param str repetitions: Number of times to play the clip, in addition to the first play (empty string = Infinity). Repetitions are ignored for loop: once. (optional)
    :param float startAt: Sets the start of an animation to a specific time (in milliseconds). This is useful when you need to jump to an exact time in an animation. The input parameter will be scaled by the mixer's timeScale. (optional)
    :param float timeScale: Scaling factor for playback speed. A value of 0 causes the animation to pause. Negative values cause the animation to play backwards. Defaults to '1' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
