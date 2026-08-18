from ..base_object import *


class Chat(BaseObject):
    """
    Chat message class. Wrapper around JSON for chat messages.

    Chat messages do not use the ``action``/``data`` payload shape of scene
    objects. The wire format is flat, matching the ARENA web client::

        {"object_id": <sender id>, "type": "chat", "dn": <display name>, "text": <message>}

    Received chat messages are handed to the ``on_chat_callback`` handler as a
    ``Chat``. Outgoing chat messages are published with ``Scene.send_chat()``,
    which fills in ``object_id`` and ``dn`` for this program.

    :param str text: Body of the chat message (required).
    :param str object_id: Id of the sending user or program (optional).
    :param str dn: Display name of the sender, as shown in the chat panel (optional).
    :param str type: Chat message type, ``"chat"`` by default (optional).
    """

    TYPE = "chat"

    def __init__(self, text="", object_id=None, dn=None, type="chat", **kwargs):
        super().__init__(object_id=object_id, type=type, dn=dn, text=text, **kwargs)
