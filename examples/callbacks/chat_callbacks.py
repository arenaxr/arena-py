"""Chat Callback

Extremely basic example of setting a chat message handler to echo
chat messages typed in the scene.

Note that currently all chat messages terminate with `\n` (newline) that should
probably be stripped.
"""

import arena


def chat_handler(_scene, chatmsg, _rawmsg):
    print(f"Chat message from {chatmsg.dn} ({chatmsg.object_id}): {chatmsg.text.strip()}")


scene = arena.Scene(host="arenaxr.org", scene="example", on_chat_callback=chat_handler)

scene.run_tasks()
