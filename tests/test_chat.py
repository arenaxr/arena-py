"""Tests for scene chat: the on_chat_callback receive path and Scene.send_chat().

The receive half shipped without tests; these pin its behavior. The send half is
new, so these also cover topic selection, wire format, and the fact that chat
payloads (which have no "data" field) bypass delta compression untouched.
"""

import json
import unittest

from arena.chat import Chat
from arena.test_system import ArenaE2ETest


def payload_of(msg):
    """Decodes a captured MockMQTTTransport message payload to a dict."""
    payload = msg["payload"]
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return json.loads(payload)


class TestChatObject(unittest.TestCase):
    """Unit tests for the Chat wrapper class."""

    def test_defaults(self):
        """A Chat built for sending has all four wire fields, type 'chat'."""
        chatmsg = Chat(text="hello")
        self.assertEqual(vars(chatmsg), {"object_id": None, "type": "chat", "dn": None, "text": "hello"})

    def test_explicit_fields(self):
        """Sender fields are settable."""
        chatmsg = Chat(text="hi", object_id="user_bob", dn="Bob")
        self.assertEqual(chatmsg.object_id, "user_bob")
        self.assertEqual(chatmsg.dn, "Bob")
        self.assertEqual(chatmsg.type, "chat")

    def test_from_received_payload(self):
        """Chat(**payload) of a received message keeps every key, including topic."""
        payload = {
            "object_id": "user_bob",
            "type": "chat",
            "dn": "Bob",
            "text": "hello\n",
            "topic": "realm/s/user/test_scene/c/someclient/user_bob",
        }
        chatmsg = Chat(**payload)
        self.assertEqual(vars(chatmsg), payload)


class TestChatReceive(unittest.IsolatedAsyncioTestCase):
    """The on_chat_callback receive path (arena/scene.py chat branch)."""

    async def _harness(self, handler=None):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        if handler is not None:
            harness.scene.on_chat_callback = handler
        # subscriptions are only registered from the async on_connect callback
        harness._start_tasks()
        await harness.run_step(0.3)
        return harness

    async def test_public_chat_delivered(self):
        """A public chat message reaches on_chat_callback as a Chat."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append((scene, chatmsg, msg)))

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello\n"},
        )
        await harness.run_step(0.3)

        self.assertEqual(len(received), 1)
        scene, chatmsg, _raw = received[0]
        self.assertIs(scene, harness.scene)
        self.assertIsInstance(chatmsg, Chat)
        self.assertEqual(chatmsg.object_id, "user_bob")
        self.assertEqual(chatmsg.type, "chat")
        self.assertEqual(chatmsg.dn, "Bob")
        self.assertEqual(chatmsg.text, "hello\n")
        # the receive path annotates the payload with its source topic
        self.assertEqual(chatmsg.topic, "realm/s/user/test_scene/c/someclient/user_bob")

    async def test_private_chat_delivered(self):
        """A chat message addressed privately to this program is delivered too."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))

        harness.inject_message(
            f"realm/s/user/test_scene/c/someclient/user_bob/{harness.scene.userid}",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "psst"},
        )
        await harness.run_step(0.3)

        self.assertEqual([chatmsg.text for chatmsg in received], ["psst"])

    async def test_chat_creates_no_scene_object(self):
        """Chat is not an object update: it must not land in scene.all_objects."""
        harness = await self._harness(lambda scene, chatmsg, msg: None)

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(0.3)

        self.assertNotIn("user_bob", harness.scene.all_objects)

    async def test_chat_dropped_without_handler(self):
        """With no on_chat_callback, chat is dropped silently and creates no object."""
        harness = await self._harness()

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(0.3)

        self.assertNotIn("user_bob", harness.scene.all_objects)

    async def test_own_chat_not_echoed_back(self):
        """Chat published by this client is filtered by the ignore_topic self-match."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))

        harness.inject_message(
            f"realm/s/user/test_scene/c/{harness.scene.userclient}/{harness.scene.userid}",
            {"object_id": harness.scene.userid, "type": "chat", "dn": "Me", "text": "mine"},
        )
        await harness.run_step(0.3)

        self.assertEqual(received, [])

    async def test_object_id_topic_mismatch_rejected(self):
        """object_id must match the topic uuid token, chat included."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_impostor", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(0.3)

        self.assertEqual(received, [])


class TestChatSend(unittest.IsolatedAsyncioTestCase):
    """Scene.send_chat() publish path."""

    def _harness(self):
        return ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")

    def _chat_messages(self, harness):
        return [msg for msg in harness.capture_published_messages() if "/c/" in msg["topic"]]

    async def test_publishes_on_public_chat_topic(self):
        """A public chat message goes out on the scene chat topic."""
        harness = self._harness()
        harness.scene.send_chat("hello scene")
        await harness.run_step(0.1)

        messages = self._chat_messages(harness)
        self.assertEqual(len(messages), 1)
        scene = harness.scene
        self.assertEqual(
            messages[0]["topic"],
            f"realm/s/user/test_scene/c/{scene.userclient}/{scene.userid}",
        )

    async def test_public_wire_format(self):
        """Payload matches the web client format: no action, no data."""
        harness = self._harness()
        harness.scene.send_chat("hello scene", display_name="Test Program")
        await harness.run_step(0.1)

        payload = payload_of(self._chat_messages(harness)[0])
        self.assertEqual(payload["object_id"], harness.scene.userid)
        self.assertEqual(payload["type"], "chat")
        self.assertEqual(payload["dn"], "Test Program")
        self.assertEqual(payload["text"], "hello scene")
        self.assertNotIn("action", payload)
        self.assertNotIn("data", payload)
        # the web client renders the send time from the payload timestamp
        self.assertIn("timestamp", payload)

    async def test_display_name_defaults_to_username(self):
        """Without display_name, the sender name is this program's ARENA username."""
        harness = self._harness()
        harness.scene.send_chat("hello scene")
        await harness.run_step(0.1)

        payload = payload_of(self._chat_messages(harness)[0])
        self.assertEqual(payload["dn"], harness.scene.username)

    async def test_private_chat_topic_includes_recipient(self):
        """A directed chat message goes out on the private chat topic."""
        harness = self._harness()
        harness.scene.send_chat("just for you", to_uid="user_bob")
        await harness.run_step(0.1)

        messages = self._chat_messages(harness)
        self.assertEqual(len(messages), 1)
        scene = harness.scene
        self.assertEqual(
            messages[0]["topic"],
            f"realm/s/user/test_scene/c/{scene.userclient}/{scene.userid}/user_bob",
        )
        self.assertEqual(payload_of(messages[0])["text"], "just for you")

    async def test_send_chat_object(self):
        """A Chat built by the caller can be published directly."""
        harness = self._harness()
        harness.scene.send_chat(Chat(text="from a Chat", dn="Bob"))
        await harness.run_step(0.1)

        payload = payload_of(self._chat_messages(harness)[0])
        self.assertEqual(payload["text"], "from a Chat")
        self.assertEqual(payload["dn"], "Bob")
        # object_id is always this program: it has to match the topic idTag token
        self.assertEqual(payload["object_id"], harness.scene.userid)

    async def test_received_chat_can_be_relayed(self):
        """Relaying a received Chat drops the receive-only topic annotation."""
        harness = self._harness()
        received = Chat(
            object_id="user_bob",
            type="chat",
            dn="Bob",
            text="relay me",
            topic="realm/s/user/test_scene/c/someclient/user_bob",
        )
        harness.scene.send_chat(received)
        await harness.run_step(0.1)

        payload = payload_of(self._chat_messages(harness)[0])
        self.assertNotIn("topic", payload)
        self.assertEqual(payload["text"], "relay me")

    async def test_permission_check_runs_for_chat_topic(self):
        """Chat has its own publish-rights pre-check, separate from objects."""
        harness = self._harness()
        # test token grants '#', so chat publishing is permitted
        self.assertTrue(harness.scene.can_publish_chat)


class TestChatDeltaCompression(unittest.IsolatedAsyncioTestCase):
    """Chat payloads have no 'data' field, so delta compression must not touch them."""

    async def test_chat_not_delta_compressed(self):
        """With delta compression on, a repeated chat message is still sent in full."""
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        # the harness disables delta compression; this test is about the on case
        harness.scene.delta_compression = True

        harness.scene.send_chat("same text")
        harness.scene.send_chat("same text")
        await harness.run_step(0.1)

        messages = [msg for msg in harness.capture_published_messages() if "/c/" in msg["topic"]]
        self.assertEqual(len(messages), 2)
        for msg in messages:
            payload = payload_of(msg)
            self.assertEqual(payload["text"], "same text")
            self.assertEqual(payload["type"], "chat")
            self.assertEqual(payload["dn"], harness.scene.username)

    async def test_chat_does_not_touch_delta_shadow_state(self):
        """Chat must not seed or clobber the object delta shadow state.

        Chat and the program's camera-like objects can share an object_id (this
        program's userid), so a chat publish leaking into _last_published_state
        would corrupt the next object delta.
        """
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        harness.scene.delta_compression = True

        harness.scene.send_chat("hello")
        await harness.run_step(0.1)

        self.assertEqual(harness.scene._last_published_state, {})


if __name__ == "__main__":
    unittest.main()
