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
    text = chatmsg.text.strip()
    print(f"Chat message from {chatmsg.dn} ({chatmsg.object_id}): {text}")
    # Reply only to an explicit command, never to every message received. Two
    # programs that each answer every chat would keep answering each other.
    if text.startswith(COMMAND):
        scene.send_chat(f"You said: {text[len(COMMAND):]}", to_uid=chatmsg.object_id)


scene = arena.Scene(host="arenaxr.org", scene="example", on_chat_callback=chat_handler)


@scene.run_once
def announce():
    scene.send_chat(f"Chat example program is here, say '{COMMAND}something'!")


scene.run_tasks()
