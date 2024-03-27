from ..utils import Utils
from .attribute import Attribute
from .position import Position
from .rotation import Rotation
from .scale import Scale

class Animation(Attribute):
    """
    Animation attribute class to manage its properties in the ARENA: Animate and tween values. More properties at <https://aframe.io/docs/1.5.0/components/animation.html> A-Frame Animation component. Easing properties are detailed at <https://easings.net> easings.net.
    Usage: `animation=Animation(...)`

    :param bool autoplay: Whether or not the animation should autoplay. Should be specified if the animation is defined for the animation-timeline component (currently not supported). Defaults to 'True' (optional)
    :param float delay: How long (milliseconds) to wait before starting. (optional)
    :param str dir: Which dir to go from from to to. Allows [normal, alternate, reverse] Defaults to 'normal' (optional)
    :param float dur: How long (milliseconds) each cycle of the animation is. Defaults to '1000' (optional)
    :param str easing: Easing function of animation. To ease in, ease out, ease in and out. See easings.net for more. Allows [easeInQuad, easeInCubic, easeInQuart, easeInQuint, easeInSine, easeInExpo, easeInCirc, easeInBack, easeInElastic, easeOutQuad, easeOutCubic, easeOutQuart, easeOutQuint, easeOutSine, easeOutExpo, easeOutCirc, easeOutBack, easeOutElastic, easeInOutQuad, easeInOutCubic, easeInOutQuart, easeInOutQuint, easeInOutSine, easeInOutExpo, easeInOutCirc, easeInOutBack, easeInOutElastic, linear] Defaults to 'easeInQuad' (optional)
    :param float elasticity: How much to bounce (higher is stronger). Defaults to '400' (optional)
    :param bool enabled: If disabled, animation will stop and startEvents will not trigger animation start. Defaults to 'True' (optional)
    :param str from: Initial value at start of animation. If not specified, the current property value of the entity will be used (will be sampled on each animation start). It is best to specify a from value when possible for stability. (optional)
    :param bool isRawProperty: Flag to animate an arbitrary object property outside of A-Frame components for better performance. If set to true, for example, we can set property to like components.material.material.opacity. If property starts with components or object3D, this will be inferred to true. (optional)
    :param str loop: How many times the animation should repeat. If the value is true, the animation will repeat infinitely. (optional)
    :param list[str] pauseEvents: Comma-separated list of events to listen to trigger pause. Can be resumed with resumeEvents. (optional)
    :param str property: Property to animate. Can be a component name, a dot-delimited property of a component (e.g., material.color), or a plain attribute. (optional)
    :param list[str] resumeEvents: Comma-separated list of events to listen to trigger resume after pausing. (optional)
    :param bool round: Whether to round values. (optional)
    :param list[str] startEvents: Comma-separated list of events to listen to trigger a restart and play. Animation will not autoplay if specified. startEvents will restart the animation, use pauseEvents to resume it. If there are other animation components on the entity animating the same property, those animations will be automatically paused to not conflict. (optional)
    :param str to: Target value at end of animation. (optional)
    :param str type: Right now only supports color for tweening isRawProperty color XYZ/RGB vector values. (optional)
    """
    def __init__(self, **kwargs):
        if "start" in kwargs:
            if isinstance(kwargs["start"], tuple) or isinstance(kwargs["start"], list):
                kwargs["start"] = Utils.tuple_to_string(kwargs["start"])
            elif isinstance(kwargs["start"], (Position, Rotation, Scale)):
                kwargs["start"] = vars(kwargs["start"])
        if "end" in kwargs:
            if isinstance(kwargs["end"], tuple) or isinstance(kwargs["end"], list):
                kwargs["end"] = Utils.tuple_to_string(kwargs["end"])
            elif isinstance(kwargs["end"], (Position, Rotation, Scale)):
                kwargs["end"] = vars(kwargs["end"])
        super().__init__(**kwargs)
