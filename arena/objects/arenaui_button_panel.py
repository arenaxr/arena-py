from .arena_object import Object


class ArenauiButtonPanel(Object):
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
        json_payload = {k: v for k, v in vars(
            self).items() if k not in skipped_keys}
        json_payload["data"]["buttons"] = [
            vars(button) if hasattr(button, "__dict__") else button
            for button in json_payload["data"]["buttons"]
        ]
        json_payload.update(kwargs)
        return json_payload


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


class ButtonPanel(ArenauiButtonPanel):
    """
    Altername name for ArenauiButtonPanel.
    """
