from ..base_object import *

_UNSET = object()  # distinguishes "argument omitted" from an explicit None


class Chat(BaseObject):
    """
    Chat message class. Wrapper around JSON for chat messages.

    Chat messages do not use the ``action``/``data`` payload shape of scene
    objects. The wire format is flat, matching the ARENA web client::

        {"object_id": <sender id>, "type": "chat", "dn": <display name>, "text": <message>}

    Only the fields actually passed in are set, so ``Chat(**payload)`` of a
    received message reproduces that payload exactly and ``"dn" in chatmsg``
    stays a usable test for whether the sender supplied a display name. The web
    client omits ``dn`` on ``chat-ctrl`` messages, for example.

    Received chat messages are handed to the ``on_chat_callback`` handler as a
    ``Chat``. Outgoing chat messages are published with ``Scene.send_chat()``,
    which fills in ``object_id``, ``type`` and ``dn`` for this program.

    :param str text: Body of the chat message. Required to publish, but omitted
        on a Chat built from a payload that carried no text (optional).
    :param str object_id: Id of the sending user or program. Overwritten with
        this program's id when published (optional).
    :param str dn: Display name of the sender, as shown in the chat panel (optional).
    :param str type: Chat message type; ``Scene.send_chat()`` defaults it to
        ``"chat"`` when it is not set (optional).
    """

    def __init__(self, text=_UNSET, object_id=_UNSET, dn=_UNSET, **kwargs):
        # Ordered to match the web client's wire format, so a Chat built for
        # sending serialises its keys in the same order.
        fields = {
            "object_id": object_id,
            "type": kwargs.pop("type", _UNSET),
            "dn": dn,
            "text": text,
        }
        super().__init__(**{k: v for k, v in fields.items() if v is not _UNSET}, **kwargs)
