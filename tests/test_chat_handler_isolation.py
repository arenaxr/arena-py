"""Tests that a raising chat handler does not stop the scene's receive loop.

Scene.process_message is the single task that drains msg_queue. Every callback
it dispatches from the object branch runs inside a try that logs and moves on,
but the chat branch used to sit ahead of that try, so an exception raised by a
user's on_chat_callback propagated out of process_message into AsyncWorker.run,
which printed the traceback and returned. The task ended there: the process and
the other workers stayed alive, so nothing announced the failure, but no
message was ever handled again for the rest of the session.

These tests therefore assert on what happens *after* the raising handler --
later chat messages, later object messages, and the queue draining -- rather
than on the exception being caught. Catching the exception is not the property
worth pinning; surviving it is.

The provoking payload is the one from the field: a "chat-ctrl" broadcast with
no "dn", which the web client publishes for its recording banner, read by a
handler that does the natural thing and reads chatmsg.dn.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite.
"""

import unittest

from arena.objects import Object
from arena.test_system import ArenaE2ETest
from arena.topics import PUBLISH_TOPICS

SCENE = "test_scene"
NAMESPACE = "user"
REALM = "realm"


def chat_topic(uuid, user_client="other_client"):
    """Topic for an inbound scene chat message from another client.

    The idTag token has to equal the payload's object_id, or
    Scene.process_message discards the message before any dispatch.
    """
    return PUBLISH_TOPICS.SCENE_CHAT.substitute(
        realm=REALM, nameSpace=NAMESPACE, sceneName=SCENE, userClient=user_client, idTag=uuid
    )


def object_topic(object_id, user_client="other_client"):
    """Topic for an inbound scene object message from another client."""
    return PUBLISH_TOPICS.SCENE_OBJECTS.substitute(
        realm=REALM, nameSpace=NAMESPACE, sceneName=SCENE, userClient=user_client, objectId=object_id
    )


class ChatHandlerIsolationTestCase(unittest.IsolatedAsyncioTestCase):
    """A user handler that raises costs that one message, and nothing more."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    async def make_harness():
        """Starts the harness and lets the mock transport register subscriptions.

        MockMQTTTransport fires on_connect on the event loop, and inject_message
        is silently dropped until the subscriptions it sets up exist.
        """
        harness = ArenaE2ETest(scene_name=SCENE, realm=REALM, namespace=NAMESPACE)
        Object.all_objects.clear()  # drop objects loaded from mock persist
        harness._start_tasks()
        for _ in range(10):
            if harness.transport.subscriptions:
                break
            await harness.run_step(0.1)
        return harness

    @staticmethod
    async def inject_ctrl_chat(harness, uuid="ctrl_uid"):
        """Injects the chat-ctrl broadcast that carries no display name.

        This is the shape the web client publishes for its recording banner, and
        the one that makes a handler reading chatmsg.dn raise AttributeError.
        """
        harness.inject_message(
            chat_topic(uuid),
            {"object_id": uuid, "type": "chat-ctrl", "text": "recording"},
        )
        await harness.run_step(0.2)

    @staticmethod
    async def inject_chat(harness, text, uuid="other_uid", dn="Someone"):
        """Injects an ordinary chat message, the kind the handler can handle."""
        harness.inject_message(
            chat_topic(uuid),
            {"object_id": uuid, "type": "chat", "text": text, "dn": dn},
        )
        await harness.run_step(0.2)

    @staticmethod
    async def inject_box_create(harness, object_id):
        """Injects an object create, to check the *object* branch still runs."""
        harness.inject_message(
            object_topic(object_id),
            {
                "object_id": object_id,
                "action": "create",
                "type": "object",
                "data": {"object_type": "box", "position": {"x": 1, "y": 1, "z": 1}},
            },
        )
        await harness.run_step(0.2)

    async def test_later_chat_is_still_handled(self):
        """The loop survives: a chat message after the raising one is handled.

        This is the regression itself. Before the guard the second injection was
        never dispatched, because the task that drains msg_queue had ended.
        """
        harness = await self.make_harness()
        handled = []

        def on_chat(scene, chatmsg, msg):
            handled.append(chatmsg.dn)  # raises on the dn-less chat-ctrl

        harness.scene.on_chat_callback = on_chat

        await self.inject_ctrl_chat(harness)
        await self.inject_chat(harness, "hello", dn="Someone")

        self.assertEqual(handled, ["Someone"])

    async def test_later_object_message_is_still_processed(self):
        """The object branch of the same loop keeps working too.

        A chat handler and object handling are unrelated features to a user, so
        a bug in one must not take the other down with it.
        """
        harness = await self.make_harness()

        def on_chat(scene, chatmsg, msg):
            handled = chatmsg.dn  # noqa: F841 -- raises on the dn-less chat-ctrl

        harness.scene.on_chat_callback = on_chat

        await self.inject_ctrl_chat(harness)
        await self.inject_box_create(harness, "later_box")

        self.assertIn("later_box", harness.scene.all_objects)

    async def test_queue_is_drained_after_a_raising_handler(self):
        """Nothing is left stranded in msg_queue.

        The queue is the direct evidence of the dead task: with the loop gone,
        every message injected afterwards simply accumulated there.
        """
        harness = await self.make_harness()

        def on_chat(scene, chatmsg, msg):
            handled = chatmsg.dn  # noqa: F841 -- raises on the dn-less chat-ctrl

        harness.scene.on_chat_callback = on_chat

        await self.inject_ctrl_chat(harness)
        await self.inject_chat(harness, "hello")
        await self.inject_box_create(harness, "later_box")

        self.assertEqual(harness.scene.msg_queue.qsize(), 0)

    async def test_every_later_chat_is_handled_not_just_the_next_one(self):
        """The loop is alive, not merely one message further along.

        A guard placed so that it swallowed the rest of one message's work would
        still pass the single-message check, so this repeats the failure and
        counts the good messages either side of it.
        """
        harness = await self.make_harness()
        handled = []

        def on_chat(scene, chatmsg, msg):
            handled.append(chatmsg.dn)  # raises on the dn-less chat-ctrl

        harness.scene.on_chat_callback = on_chat

        await self.inject_chat(harness, "first", dn="A")
        await self.inject_ctrl_chat(harness)
        await self.inject_chat(harness, "second", dn="B")
        await self.inject_ctrl_chat(harness, uuid="ctrl_uid_2")
        await self.inject_chat(harness, "third", dn="C")

        self.assertEqual(handled, ["A", "B", "C"])

    async def test_raising_handler_does_not_reach_the_program(self):
        """The exception is reported, not raised at the user's program.

        process_message has no caller that could handle it -- AsyncWorker.run
        just prints and returns -- so there is nowhere for it to usefully go.
        """
        harness = await self.make_harness()

        def on_chat(scene, chatmsg, msg):
            raise RuntimeError("handler blew up")

        harness.scene.on_chat_callback = on_chat

        # no assertRaises: the injection and the steps must simply complete
        await self.inject_chat(harness, "hello")
        await self.inject_chat(harness, "hello again")

        self.assertEqual(harness.scene.msg_queue.qsize(), 0)

    async def test_malformed_chat_payload_does_not_stop_the_loop(self):
        """The Chat(**payload) construction is inside the guard as well.

        The payload is a remote sender's, so its shape is not something this
        client controls; a payload that Chat cannot be built from must cost the
        same as a handler that raises.
        """
        harness = await self.make_harness()
        handled = []
        harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)

        # "data" is not a chat field; Chat treats it as the payload body, and a
        # string there is not something it can build attributes from
        harness.inject_message(
            chat_topic("bad_uid"),
            {"object_id": "bad_uid", "type": "chat", "data": "not-a-dict"},
        )
        await harness.run_step(0.2)
        await self.inject_chat(harness, "hello")

        self.assertEqual(handled, ["hello"])
        self.assertEqual(harness.scene.msg_queue.qsize(), 0)

    async def test_good_chat_handler_is_unaffected(self):
        """The ordinary path is untouched: no guard, no swallowing, no change.

        Cheap to state, and it is what keeps the fix from being a behaviour
        change for every program that does not have this bug.
        """
        harness = await self.make_harness()
        handled = []
        harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)

        await self.inject_chat(harness, "hello")

        self.assertEqual(handled, ["hello"])


if __name__ == "__main__":
    unittest.main()
