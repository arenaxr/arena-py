from .attribute import Attribute


class ClickListener(Attribute):
    """
    ClickListener attribute class to manage its properties in the ARENA: Object will listen for mouse events like clicks.
    Usage: `click_listener=ClickListener(...)` or `clickable=True`

    :param bool bubble: Set false to prevent click events from bubbling up to parent objects. See <https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events#event_bubbling> Event Bubbling. Defaults to 'True' (optional)
    :param bool enabled: Publish events, set false to disable. Defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
