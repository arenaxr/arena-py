"""Tests for scene chat: the on_chat_callback receive path and Scene.send_chat().

The receive half shipped without tests; these pin its behavior, including the
fact that a received Chat reproduces its wire payload exactly. The send half is
new, so these also cover topic selection, wire format, input validation, the
self-echo guards that keep a replying handler from looping, and the fact that
chat payloads (which have no "data" field) bypass delta compression untouched.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from arena.attributes import Position, Rotation, Scale
from arena.chat import Chat
from arena.objects import Box
from arena.test_system import ArenaE2ETest
from arena.transport import MockMQTTTransport

# Long enough for the mock transport's on_connect hop and the message queue to
# drain, short enough that the whole module stays cheap.
STEP = 0.05


def payload_of(msg):
    """Decodes a captured MockMQTTTransport message payload to a dict."""
    payload = msg["payload"]
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return json.loads(payload)


def chat_messages(harness):
    """Captured publishes on the chat topic branch."""
    return [msg for msg in harness.capture_published_messages() if "/c/" in msg["topic"]]


class LoopbackTransport(MockMQTTTransport):
    """A mock transport that reflects publishes back, the way a broker does.

    MockMQTTTransport.publish() only records, so a message this client publishes
    is never delivered to this client's own subscriptions. Real MQTT 3.1.1
    brokers do deliver it -- that reflection is the reason ArenaMQTT keeps an
    ignore_topic at all -- and without modelling it a self-echo loop cannot be
    observed in a test. The cap keeps a genuine runaway loop from hanging the
    suite while still recording that it ran away.
    """

    PUBLISH_CAP = 25

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hit_publish_cap = False

    def publish(self, topic, payload, qos=0):
        result = super().publish(topic, payload, qos)
        if len(self.published_messages) > self.PUBLISH_CAP:
            self.hit_publish_cap = True  # runaway: stop feeding the loop
            return result
        if not isinstance(payload, bytes):
            payload = str(payload).encode("utf-8")
        self.mock_receive(topic, payload)
        return result


class TestChatObject(unittest.TestCase):
    """Unit tests for the Chat wrapper class."""

    def test_only_given_fields_are_set(self):
        """Chat sets exactly the fields passed in; send_chat fills the rest."""
        self.assertEqual(vars(Chat(text="hello")), {"text": "hello"})

    def test_explicit_fields(self):
        """Sender fields are settable, including a non-default type."""
        chatmsg = Chat(text="hi", object_id="user_bob", dn="Bob")
        self.assertEqual(chatmsg.object_id, "user_bob")
        self.assertEqual(chatmsg.dn, "Bob")
        self.assertEqual(vars(Chat(text="logout", type="chat-ctrl"))["type"], "chat-ctrl")

    def test_from_received_payload(self):
        """Chat(**payload) of a received message keeps every key, including topic."""
        payload = {
            "object_id": "user_bob",
            "type": "chat",
            "dn": "Bob",
            "text": "hello\n",
            "topic": "realm/s/user/test_scene/c/someclient/user_bob",
        }
        self.assertEqual(vars(Chat(**payload)), payload)

    def test_omitted_fields_are_not_injected(self):
        """A payload the wire did not carry a 'dn' for must not gain one.

        The web client publishes chat-ctrl with no dn, so "dn" in chatmsg has to
        stay a usable test for whether the sender supplied a display name.
        """
        payload = {"object_id": "user_bob", "type": "chat-ctrl", "text": "sound:off"}
        chatmsg = Chat(**payload)
        self.assertEqual(vars(chatmsg), payload)
        self.assertNotIn("dn", chatmsg)

    def test_explicit_none_is_kept(self):
        """An explicitly passed None is a value, not an omission."""
        self.assertEqual(vars(Chat(text="hi", dn=None)), {"dn": None, "text": "hi"})


class TestChatReceive(unittest.IsolatedAsyncioTestCase):
    """The on_chat_callback receive path (arena/scene.py chat branch)."""

    async def _harness(self, handler=None):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        if handler is not None:
            harness.scene.on_chat_callback = handler
        # subscriptions are only registered from the async on_connect callback
        harness._start_tasks()
        await harness.run_step(STEP)
        return harness

    async def test_public_chat_delivered(self):
        """A public chat message reaches on_chat_callback as a Chat."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append((scene, chatmsg, msg)))

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello\n"},
        )
        await harness.run_step(STEP)

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
        await harness.run_step(STEP)

        self.assertEqual([chatmsg.text for chatmsg in received], ["psst"])

    async def test_chat_ctrl_without_dn_delivered_unchanged(self):
        """Through the real receive path, a payload with no dn keeps none.

        The web client's chat-ctrl messages carry no dn, and a handler that tests
        for one has to be able to tell it apart from a dn that was sent as null.
        """
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))
        payload = {"object_id": "user_bob", "type": "chat-ctrl", "text": "sound:off"}

        harness.inject_message("realm/s/user/test_scene/c/someclient/user_bob", dict(payload))
        await harness.run_step(STEP)

        self.assertEqual(len(received), 1)
        delivered = vars(received[0]).copy()
        delivered.pop("topic")
        self.assertEqual(delivered, payload)
        self.assertNotIn("dn", received[0])

    async def test_chat_creates_no_scene_object(self):
        """Chat is not an object update: it must not land in scene.all_objects."""
        harness = await self._harness(lambda scene, chatmsg, msg: None)

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(STEP)

        self.assertNotIn("user_bob", harness.scene.all_objects)

    async def test_chat_dropped_without_handler(self):
        """With no on_chat_callback, chat is dropped silently and creates no object."""
        harness = await self._harness()

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(STEP)

        self.assertNotIn("user_bob", harness.scene.all_objects)

    async def test_own_public_chat_not_echoed_back(self):
        """Chat we published publicly is filtered by the ignore_topic self-match."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))

        harness.inject_message(
            f"realm/s/user/test_scene/c/{harness.scene.userclient}/{harness.scene.userid}",
            {"object_id": harness.scene.userid, "type": "chat", "dn": "Me", "text": "mine"},
        )
        await harness.run_step(STEP)

        self.assertEqual(received, [])

    async def test_own_private_chat_not_delivered(self):
        """Chat carrying our own object_id is dropped on the private path too.

        ignore_topic only covers the public subscription, and on_message_private
        does not self-filter, so the chat branch has to reject our own id itself
        the way the web client does.
        """
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))
        userid = harness.scene.userid

        harness.inject_message(
            f"realm/s/user/test_scene/c/{harness.scene.userclient}/{userid}/{userid}",
            {"object_id": userid, "type": "chat", "dn": "Me", "text": "mine"},
        )
        # same shape, but from someone else's client id: still our own object_id
        harness.inject_message(
            f"realm/s/user/test_scene/c/otherclient/{userid}/{userid}",
            {"object_id": userid, "type": "chat", "dn": "Me", "text": "spoofed"},
        )
        await harness.run_step(STEP)

        self.assertEqual(received, [])

    async def test_object_id_topic_mismatch_rejected(self):
        """object_id must match the topic uuid token, chat included."""
        received = []
        harness = await self._harness(lambda scene, chatmsg, msg: received.append(chatmsg))

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_impostor", "type": "chat", "dn": "Bob", "text": "hello"},
        )
        await harness.run_step(STEP)

        self.assertEqual(received, [])


class TestChatSelfEchoLoop(unittest.IsolatedAsyncioTestCase):
    """A handler that replies to the sender must not be able to loop.

    Our own private chat topic (.../c/{userClient}/{idTag}/{toUid} with toUid ==
    our idTag) is matched by our own private subscription (.../+/+/+/{idTag}/#),
    the broker reflects our publishes back to us, and on_message_private does not
    self-filter. These tests reflect publishes so the loop is observable.
    """

    async def _loopback_harness(self):
        with patch("arena.test_system.MockMQTTTransport", LoopbackTransport):
            harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        self.assertIsInstance(harness.transport, LoopbackTransport)

        replies = []

        def echo_handler(scene, chatmsg, _msg):
            # the shipped example's shape: reply privately to whoever sent it
            replies.append(chatmsg.text)
            scene.send_chat(f"You said: {chatmsg.text}", to_uid=chatmsg.object_id)

        harness.scene.on_chat_callback = echo_handler
        harness._start_tasks()
        await harness.run_step(STEP)
        return harness, replies

    async def test_self_addressed_chat_does_not_loop(self):
        """Sending to our own userid must not come back and re-trigger the handler."""
        harness, replies = await self._loopback_harness()

        harness.scene.send_chat("ping", to_uid=harness.scene.userid)
        await harness.run_step(0.3)

        self.assertFalse(
            harness.transport.hit_publish_cap,
            f"runaway chat loop: {len(harness.transport.published_messages)} publishes",
        )
        self.assertEqual(replies, [])
        self.assertEqual(chat_messages(harness), [])

    async def test_foreign_chat_tagged_with_our_userid_does_not_loop(self):
        """One injected message must not induce a loop.

        ARENA ACLs constrain the userClient topic token, not the idTag token, so
        another client can publish a chat whose idTag and object_id are ours.
        """
        harness, replies = await self._loopback_harness()
        userid = harness.scene.userid

        harness.inject_message(
            f"realm/s/user/test_scene/c/someotherclient/{userid}/{userid}",
            {"object_id": userid, "type": "chat", "dn": "Somebody", "text": "boom"},
        )
        await harness.run_step(0.3)

        self.assertFalse(
            harness.transport.hit_publish_cap,
            f"runaway chat loop: {len(harness.transport.published_messages)} publishes",
        )
        self.assertEqual(replies, [])
        self.assertEqual(chat_messages(harness), [])

    async def test_replying_to_another_sender_still_works(self):
        """The guards must not break the point of the feature: replying to a peer."""
        harness, replies = await self._loopback_harness()

        harness.inject_message(
            "realm/s/user/test_scene/c/someclient/user_bob",
            {"object_id": "user_bob", "type": "chat", "dn": "Bob", "text": "hi"},
        )
        await harness.run_step(0.3)

        self.assertFalse(harness.transport.hit_publish_cap)
        self.assertEqual(replies, ["hi"])
        messages = chat_messages(harness)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0]["topic"],
            f"realm/s/user/test_scene/c/{harness.scene.userclient}/{harness.scene.userid}/user_bob",
        )
        self.assertEqual(payload_of(messages[0])["text"], "You said: hi")


class TestChatSend(unittest.IsolatedAsyncioTestCase):
    """Scene.send_chat() publish path."""

    def _harness(self):
        return ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")

    async def test_publishes_on_public_chat_topic(self):
        """A public chat message goes out on the scene chat topic."""
        harness = self._harness()
        harness.scene.send_chat("hello scene")
        await harness.run_step(0)

        messages = chat_messages(harness)
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
        await harness.run_step(0)

        payload = payload_of(chat_messages(harness)[0])
        self.assertEqual(payload["object_id"], harness.scene.userid)
        self.assertEqual(payload["type"], "chat")
        self.assertEqual(payload["dn"], "Test Program")
        self.assertEqual(payload["text"], "hello scene")
        self.assertNotIn("action", payload)
        self.assertNotIn("data", payload)

    async def test_timestamp_is_parseable_utc_milliseconds(self):
        """The web chat panel renders this timestamp, so it has to parse.

        An ISO string carrying both a numeric offset and a "Z" (what
        isoformat()[:-3] + "Z" produces for an aware datetime) is not a valid
        date to the web client and renders as "Invalid Date".
        """
        harness = self._harness()
        harness.scene.send_chat("hello scene")
        await harness.run_step(0)

        timestamp = payload_of(chat_messages(harness)[0])["timestamp"]
        self.assertRegex(timestamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
        self.assertNotIn("+", timestamp)
        # a single trailing Z, and nothing else offset-like
        self.assertEqual(timestamp.count("Z"), 1)

    async def test_display_name_defaults_to_username(self):
        """Without display_name, the sender name is this program's ARENA username."""
        harness = self._harness()
        harness.scene.send_chat("hello scene")
        await harness.run_step(0)

        payload = payload_of(chat_messages(harness)[0])
        self.assertEqual(payload["dn"], harness.scene.username)

    async def test_private_chat_topic_includes_recipient(self):
        """A directed chat message goes out on the private chat topic."""
        harness = self._harness()
        harness.scene.send_chat("just for you", to_uid="user_bob")
        await harness.run_step(0)

        messages = chat_messages(harness)
        self.assertEqual(len(messages), 1)
        scene = harness.scene
        self.assertEqual(
            messages[0]["topic"],
            f"realm/s/user/test_scene/c/{scene.userclient}/{scene.userid}/user_bob",
        )
        self.assertEqual(payload_of(messages[0])["text"], "just for you")

    async def test_send_chat_to_self_is_refused(self):
        """Addressing ourselves is a loop, not a message: nothing is published."""
        harness = self._harness()

        self.assertIsNone(harness.scene.send_chat("hello me", to_uid=harness.scene.userid))
        await harness.run_step(0)

        self.assertEqual(chat_messages(harness), [])

    async def test_send_chat_object(self):
        """A Chat built by the caller can be published directly."""
        harness = self._harness()
        harness.scene.send_chat(Chat(text="from a Chat", dn="Bob"))
        await harness.run_step(0)

        payload = payload_of(chat_messages(harness)[0])
        self.assertEqual(payload["text"], "from a Chat")
        self.assertEqual(payload["dn"], "Bob")
        # object_id is always this program: it has to match the topic idTag token
        self.assertEqual(payload["object_id"], harness.scene.userid)
        # type is filled in for a Chat that did not set one
        self.assertEqual(payload["type"], "chat")

    async def test_send_chat_keeps_custom_type(self):
        """A Chat that sets its own type keeps it."""
        harness = self._harness()
        harness.scene.send_chat(Chat(text="sound:off", type="chat-ctrl"))
        await harness.run_step(0)

        self.assertEqual(payload_of(chat_messages(harness)[0])["type"], "chat-ctrl")

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
        await harness.run_step(0)

        payload = payload_of(chat_messages(harness)[0])
        self.assertNotIn("topic", payload)
        self.assertEqual(payload["text"], "relay me")

    async def test_send_chat_does_not_mutate_the_caller_chat(self):
        """The sender fields are filled on a copy, so a relayed Chat survives."""
        harness = self._harness()
        payload = {
            "object_id": "user_bob",
            "type": "chat",
            "dn": "Bob",
            "text": "relay me",
            "topic": "realm/s/user/test_scene/c/someclient/user_bob",
        }
        received = Chat(**payload)

        harness.scene.send_chat(received)
        harness.scene.send_chat(received, to_uid="user_carol")
        await harness.run_step(0)

        self.assertEqual(vars(received), payload)
        # and a Chat with no dn does not acquire one from the send
        bare = Chat(text="bare")
        harness.scene.send_chat(bare)
        self.assertEqual(vars(bare), {"text": "bare"})

    async def test_text_must_be_text(self):
        """A null or structured body breaks the receiving web chat panel."""
        harness = self._harness()
        for bad in (None, {"a": 1}, ["a"], object()):
            with self.subTest(text=type(bad).__name__):
                with self.assertRaises(TypeError):
                    harness.scene.send_chat(bad)
        # also when it arrives inside a Chat
        with self.assertRaises(TypeError):
            harness.scene.send_chat(Chat(text=None))
        with self.assertRaises(TypeError):
            harness.scene.send_chat(Chat())
        await harness.run_step(0)

        self.assertEqual(chat_messages(harness), [])

    async def test_number_text_is_converted(self):
        """Numbers are a natural thing to chat, so they are stringified."""
        harness = self._harness()
        harness.scene.send_chat(42)
        harness.scene.send_chat(1.5)
        await harness.run_step(0)

        self.assertEqual([payload_of(m)["text"] for m in chat_messages(harness)], ["42", "1.5"])

    async def test_to_uid_must_be_a_single_topic_token(self):
        """A wildcard or empty recipient would corrupt the publish topic."""
        harness = self._harness()
        for bad in ("#", "+", "", "a/b", 7):
            with self.subTest(to_uid=bad):
                with self.assertRaises(ValueError):
                    harness.scene.send_chat("hello", to_uid=bad)
        await harness.run_step(0)

        self.assertEqual(chat_messages(harness), [])

    async def test_permission_check_runs_for_chat_topic(self):
        """Chat has its own publish-rights pre-check, separate from objects."""
        harness = self._harness()
        scene = harness.scene
        # the test token grants '#', so nothing should be reported
        scene.telemetry.set_error = MagicMock()
        scene.send_chat("allowed")
        scene.telemetry.set_error.assert_not_called()

        # a token without chat rights must be reported, naming the chat topic
        scene.can_publish_chat = False
        scene.can_publish_obj = True
        scene.send_chat("denied")
        scene.telemetry.set_error.assert_called_once()
        reported = scene.telemetry.set_error.call_args[0][0]
        self.assertIn("do not have permission", reported)
        self.assertIn(f"/c/{scene.userclient}/{scene.userid}", reported)

        # object publishing rights are a separate switch and must not be consulted
        scene.telemetry.set_error.reset_mock()
        scene.can_publish_chat = True
        scene.can_publish_obj = False
        scene.send_chat("allowed again")
        scene.telemetry.set_error.assert_not_called()
        await harness.run_step(0)


class TestChatDeltaCompression(unittest.IsolatedAsyncioTestCase):
    """Chat payloads have no 'data' field, so delta compression must not touch them."""

    def _harness(self):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        # the harness disables delta compression; these tests are about the on case
        harness.scene.delta_compression = True
        return harness

    async def test_chat_not_delta_compressed(self):
        """With delta compression on, a repeated chat message is still sent in full."""
        harness = self._harness()

        harness.scene.send_chat("same text")
        harness.scene.send_chat("same text")
        await harness.run_step(0)

        messages = chat_messages(harness)
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
        harness = self._harness()

        harness.scene.send_chat("hello")
        await harness.run_step(0)

        self.assertEqual(harness.scene._last_published_state, {})

    async def test_custom_payload_publishes_are_not_delta_compressed(self):
        """The custom_payload delta guard protects partial payloads generally.

        delete_attributes() publishes a partial data patch. Diffing that against
        the last full object state would emit deletions for every key the patch
        omits, silently deleting attributes the caller never named.
        """
        harness = self._harness()
        box = Box(
            object_id="delta_box",
            position=Position(1, 2, 3),
            scale=Scale(1, 1, 1),
            rotation=Rotation(0, 0, 0, 1),
        )
        harness.scene.add_object(box)
        harness.scene.update_object(box, position=Position(4, 5, 6))
        harness.scene.delete_attributes(box, ["scale"])
        await harness.run_step(0)

        published = [payload_of(msg) for msg in harness.capture_published_messages() if "/o/" in msg["topic"]]
        self.assertEqual(published[-1]["data"], {"scale": None})


if __name__ == "__main__":
    unittest.main()
