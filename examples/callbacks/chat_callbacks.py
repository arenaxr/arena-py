"""Chat Callback

Extremely basic example of setting a chat message handler to echo chat messages
typed in the scene, and replying with `scene.send_chat()`. It answers only the
`!echo` command, so it cannot end up in a reply loop with another program.

Note that currently all chat messages terminate with `\n` (newline) that should
probably be stripped.
"""

import arena

COMMAND = "!echo "


def chat_handler(scene, chatmsg, _rawmsg):
    # Only fields the sender actually sent are set, so test before reading one:
    # the web client's `chat-ctrl` control messages arrive on this same topic
    # branch, and they carry neither a display name nor, in some cases, any text.
    # A field can also arrive explicitly null, which Chat keeps as a value rather
    # than an omission, so a presence check alone still hands back None. Check for
    # both, the way `Scene.send_chat` does before it normalises these two fields.
    text = chatmsg.text.strip() if "text" in chatmsg and chatmsg.text is not None else ""
    sender = chatmsg.dn if "dn" in chatmsg and chatmsg.dn is not None else chatmsg.object_id
    print(f"Chat message from {sender} ({chatmsg.object_id}): {text}")
    # Reply only to an explicit command, never to every message received. Two
    # programs that each answer every chat would keep answering each other.
    if text.startswith(COMMAND):
        scene.send_chat(f"You said: {text[len(COMMAND):]}", to_uid=chatmsg.object_id)


scene = arena.Scene(host="arenaxr.org", scene="example", on_chat_callback=chat_handler)


@scene.run_once
def announce():
    scene.send_chat(f"Chat example program is here, say '{COMMAND}something'!")


scene.run_tasks()
