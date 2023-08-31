from .arena_object import Object


class Button:
    """
    Buttons of a ButtonPanel in the ARENA UI.

    :param str name: Button Name
    :param str img: Image URl for image buttons (optional)
    :param float size: Size of image button (optional)
    :param float height: Height of image button, overrides size (optional)
    :param float: Width of image button, overrides size (optional)
    :param float borderRadius: Border radius of image button (optional)
    """

    def __init__(self, name="Button", **kwargs):
        self.name = name
        self.__dict__.update(kwargs)


class ButtonPanel(Object):
    """
    Button Panel in the ARENA UI.

    :param list[Button] buttons: List of Button objects
    :param str title: Title of Button Panel (optional)
    :param bool vertical: Whether to display buttons vertically (optional)
    :param str font: Font of button panel ['Roboto', 'Roboto-Mono'] (optional)
    """

    object_type = "arenaui-button-panel"

    def __init__(self, **kwargs):
        super().__init__(object_type=ButtonPanel.object_type, **kwargs)

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        skipped_keys = [
            "evt_handler",
            "update_handler",
            "animations",
            "delayed_prop_tasks",
        ]
        json_payload = {k: v for k, v in vars(self).items() if k not in skipped_keys}
        json_payload["data"]["buttons"] = [
            vars(button) if hasattr(button, "__dict__") else button
            for button in json_payload["data"]["buttons"]
        ]
        json_payload.update(kwargs)
        return json_payload


class Prompt(Object):
    """
    Popup Prompt in the ARENA UI.

    :param str title: Title of Prompt (optional)
    :param str description: Additional desc text of prompt (optional)
    :param list[str] buttons: List of button name strings (optional)
    :param str width: Width of prompt (optional)
    :param str font: Font of button panel ['Roboto', 'Roboto-Mono'] (optional)
    """

    object_type = "arenaui-prompt"

    def __init__(self, **kwargs):
        super().__init__(object_type=Prompt.object_type, **kwargs)


class Card(Object):
    """
    Text/Image Card in the ARENA UI.

    :param str title: Title of Card (optional)
    :param str body: Body text of Card (optional)
    :param str bodyAlign: Text alignment of body text ['center', 'left', 'right', 'justify'] (optional)
    :param str img: Image URL of Card (optional)
    :param str imgCaption: Image caption (optional)
    :param str imgDirection: Left or Right image placement vs body text [ 'left', 'right'] (optional)
    :param str imgSize: Container size fitting of image ['cover', 'contain'] (optional)
    :param float fontSize: Font size of card, scales both title and body (optional)
    :param float widthScale: Width of card as a factor of the default (optional)
    :param bool closeButton: Whether to display a close button (optional)
    :param str font: Font of card ['Roboto', 'Roboto-Mono'] (optional)
    """

    object_type = "arenaui-card"

    def __init__(self, **kwargs):
        super().__init__(object_type=Card.object_type, **kwargs)
