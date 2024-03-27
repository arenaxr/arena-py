from .attribute import Attribute

class Sound(Attribute):
    """
    Sound attribute class to manage its properties in the ARENA: The sound component defines the entity as a source of sound or audio. The sound component is positional and is thus affected by the component's position. More properties at <https://aframe.io/docs/1.5.0/components/sound.html> A-Frame Sound.
    Usage: `sound=Sound(...)`

    :param bool autoplay: Whether to automatically play sound once set. (optional)
    :param str distanceModel: Sound model. Allows [linear, inverse, exponential] Defaults to 'inverse' (optional)
    :param bool loop: Whether to loop the sound once the sound finishes playing. (optional)
    :param float maxDistance: Maximum distance between the audio source and the listener, after which the volume is not reduced any further. Defaults to '10000' (optional)
    :param str on: An event for the entity to listen to before playing sound. Allows [mousedown, mouseup, mouseenter, mouseleave, triggerdown, triggerup, gripdown, gripup, menudown, menuup, systemdown, systemup, trackpaddown, trackpadup] Defaults to 'mousedown' (optional)
    :param float poolSize: Numbers of simultaneous instances of this sound that can be playing at the same time. Defaults to '1' (optional)
    :param bool positional: Whether or not the audio is positional (movable). Defaults to 'True' (optional)
    :param float refDistance: Reference distance for reducing volume as the audio source moves further from the listener. Defaults to '1' (optional)
    :param float rolloffFactor: Describes how quickly the volume is reduced as the source moves away from the listener. Defaults to '1' (optional)
    :param str src: URL path to sound file e.g. 'store/users/wiselab/sound/wave.mp3'. (optional)
    :param float volume: How loud to play the sound. Defaults to '1' (optional)
    """
    def __init__(self, src, positional=False, **kwargs):
        super().__init__(src=src, positional=positional, **kwargs)
