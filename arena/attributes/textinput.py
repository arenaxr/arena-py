from .attribute import Attribute


class Textinput(Attribute):
    """
    Textinput attribute class to manage its properties in the ARENA: Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires `click-listener` attribute.
    Usage: `textinput=Textinput(...)`

    :param list[str] inputOptions: Array of options for select or radio input types Defaults to '[]' (optional)
    :param str inputType: Type of HTML form input Allows [text, email, password, number, tel, range, textarea, url, select, radio, checkbox, date, datetime-local, time, week, month] Defaults to 'text' (optional)
    :param str inputValue: Input field initial value. Select type will be selected value, for checkbox will be checked state Defaults to '' (optional)
    :param str label: Label for input (max 140 characters, optional). Defaults to '' (optional)
    :param str on: A case-sensitive string representing the event type to listen for. See <https://developer.mozilla.org/en-US/docs/Web/Events> Web Events Allows [mousedown, mouseup, mouseenter, mouseleave, triggerdown, triggerup, gripdown, gripup, menudown, menuup, systemdown, systemup, trackpaddown, trackpadup] Defaults to 'mousedown' (optional)
    :param str placeholder: Text input placeholder (optional). Defaults to '' (optional)
    :param str title: The prompt title (optional). Defaults to '' (optional)
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
