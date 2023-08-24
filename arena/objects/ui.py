from .arena_object import Object


class Button:
    """
    Class for Buttons of a ButtonPanel in the ARENA UI.
    """

    def __init__(self, name="Button", **kwargs):
        """
        :param str name: Button Name
        :param str img: Image URl for image buttons (optional)
        :param float size: Size of image button (optional)
        :param float height: Height of image button, overrides size (optional)
        :param float: Width of image button, overrides size (optional)
        :param float borderRadius: Border radius of image button (optional)
        """
        self.name = name
        self.__dict__.update(kwargs)


class ButtonPanel(Object):
    """
    Class for Button Panels in the ARENA UI.
    """
    object_type = "arenaui-button-panel"

    def __init__(self, **kwargs):
        """
        :param list[Button] buttons: List of Button objects
        :param str title: Title of Button Panel (optional)
        :param bool vertical: Whether to display buttons vertically (optional)
        :param str font: Font of button panel ['Roboto', 'Roboto-Mono'] (optional)
        """
        self.buttons = []
        super().__init__(object_type=ButtonPanel.object_type, **kwargs)

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        json_payload = {k: v for k, v in vars(self).items() if k != "buttons"}
        json_payload["buttons"] = [vars(button) for button in self.buttons]
        json_payload.update(kwargs)
        return json_payload


class Prompt(Object):
    """
    Class for popup Prompts in the ARENA UI.
    """
    object_type = "arenaui-prompt"

    def __init__(self, **kwargs):
        """
        :param str title: Title of Prompt (optional)
        :param str description: Additional desc text of prompt (optional)
        :param list[str] buttons: List of button name strings (optional)
        :param str width: Width of prompt (optional)
        :param str font: Font of button panel ['Roboto', 'Roboto-Mono'] (optional)
        """
        super().__init__(object_type=Prompt.object_type, **kwargs)


class Card(Object):
    """
    Class for Text/Image Cards in the ARENA UI.
    """
    object_type = "arenaui-card"

    def __init__(self, **kwargs):
        """
        :param str title: Title of Card (optional)
        :param str body: Body text of Card (optional)
        :param str bodyAlign: Text alignment of body text ['center', 'left', 'right', 'justify'] (optional)
        :param str img: Image URL of Card (optional)
        :param str imgCaption: Image caption (optional)
        :param str imgAlign: Left or Right image alignment vs body text [ 'left', 'right'] (optional)
        :param float fontSize: Font size of card, scales both title and body (optional)
        :param float widthScale: Width of card as a factor of the default (optional)
        :param bool closeButton: Whether to display a close button (optional)
        :param str font: Font of card ['Roboto', 'Roboto-Mono'] (optional)
        """
        super().__init__(object_type=Card.object_type, **kwargs)
