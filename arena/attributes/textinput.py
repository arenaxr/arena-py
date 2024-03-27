from .attribute import Attribute


class Textinput(Attribute):
    """
    Textinput attribute class to manage its properties in the ARENA: Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires click-listener.
    Usage: `textinput=Textinput(...)`

    :param str label: Text prompt label Defaults to 'Input text below (max is 140 characters).' (optional)
    :param str on: A case-sensitive string representing the event type to listen for. See <https://developer.mozilla.org/en-US/docs/Web/Events> Web Events Allows [mousedown, mouseup, mouseenter, mouseleave, triggerdown, triggerup, gripdown, gripup, menudown, menuup, systemdown, systemup, trackpaddown, trackpadup] Defaults to 'mousedown' (optional)
    :param str placeholder: Text input place holder. Defaults to 'Type here' (optional)
    :param str title: The prompt title. Defaults to 'Text Input' (optional)
    """

    def __init__(self,
                 title="Text Input",
                 label="Input text below (max is 140 characters)",
                 placeholder="Type here",
                 on="mousedown",
                 **kwargs):
        super().__init__(title=title[:140], label=label[:140],
                         placeholder=placeholder[:140], on=on, **kwargs)


class TextInput(Textinput):
    """
    Alternate name for Textinput.
    Usage: `textinput=TextInput(...)`
    """
