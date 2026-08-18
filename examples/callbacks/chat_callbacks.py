"""Chat Callback

Extremely basic example of setting a chat message handler to echo
chat messages typed in the scene, and replying with `scene.send_chat()`.

Note that currently all chat messages terminate with `\n` (newline) that should
probably be stripped.
"""

import arena


def chat_handler(scene, chatmsg, _rawmsg):
    print(f"Chat message from {chatmsg.dn} ({chatmsg.object_id}): {chatmsg.text.strip()}")
    # reply privately to the sender; omit to_uid to reply to the whole scene
    scene.send_chat(f"You said: {chatmsg.text.strip()}", to_uid=chatmsg.object_id)


scene = arena.Scene(host="arenaxr.org", scene="example", on_chat_callback=chat_handler)


@scene.run_once
def announce():
    scene.send_chat("Chat example program is here, say something!")


scene.run_tasks()
