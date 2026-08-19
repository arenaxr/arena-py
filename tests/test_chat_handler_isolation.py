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

import asyncio
import contextlib
import io
import unittest

from arena.objects import Object
from arena.test_system import ArenaE2ETest
from arena.topics import PUBLISH_TOPICS

SCENE = "test_scene"
NAMESPACE = "user"
REALM = "realm"


class _BaseExc(BaseException):
    """A BaseException the asyncio machinery has no special handling for."""


def receive_loop_task(scene):
    """The single live asyncio task running scene.process_message.

    Picked out by identity rather than by "the only task that finished", so a
    harness that grows another short-lived task cannot make a test read a
    surviving guard as a swallowed exception. Each of the harness's tasks is an
    AsyncWorker.run frame whose `self.func` is the bound method it drives, so a
    running task is identifiable while its frame is still alive -- call this
    before the exception under test, not after.
    """
    for task in asyncio.all_tasks():
        frame = task.get_coro().cr_frame
        worker = frame.f_locals.get("self") if frame else None
        if getattr(worker, "func", None) == scene.process_message:
            return task
    raise AssertionError("no live task is running scene.process_message")


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
        """Starts the harness and waits for the mock transport's subscriptions.

        MockMQTTTransport fires on_connect on the event loop, and inject_message
        is silently dropped until the subscriptions it sets up exist, so the
        harness polls for them and fails loudly if they never arrive.
        """
        harness = ArenaE2ETest(scene_name=SCENE, realm=REALM, namespace=NAMESPACE)
        Object.all_objects.clear()  # drop objects loaded from mock persist
        await harness.start_and_wait_until_subscribed()
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

    async def test_chat_construction_failure_does_not_stop_the_loop(self):
        """The Chat(**payload) construction is inside the guard as well.

        Chat keeps every field optional -- text, object_id, dn and type all
        default to unset -- so almost any payload builds. A payload the *handler*
        then chokes on would be caught by the guard even with the construction
        left outside it, and so would not pin the placement.

        A JSON object carrying a "self" key is the case that does. It reaches
        Chat.__init__ as a second binding for the bound-method receiver:

            TypeError: Chat.__init__() got multiple values for argument 'self'

        The key is legal JSON and legal for the topic's object_id check, so any
        sender can put it on a scene chat topic. With Chat(**payload) outside
        the try that TypeError leaves process_message and ends the task draining
        msg_queue -- exactly the failure this branch is about -- so this test
        fails unless the construction is guarded too.
        """
        harness = await self.make_harness()
        handled = []
        harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)

        harness.inject_message(
            chat_topic("bad_uid"),
            {"object_id": "bad_uid", "type": "chat", "self": 1},
        )
        await harness.run_step(0.2)
        await self.inject_chat(harness, "hello")

        self.assertEqual(handled, ["hello"])
        self.assertEqual(harness.scene.msg_queue.qsize(), 0)

    async def test_the_failing_chat_payload_is_reported(self):
        """Surviving quietly is not enough: the failure has to be visible.

        The guard is a broad `except`, and the justification for one that broad
        is that it reports rather than swallows -- otherwise a handler bug turns
        into messages that vanish with no trace, which is harder to diagnose
        than the crash it replaced. So pin the report, not just the survival:
        the payload that provoked it has to reach stderr, since without it a
        user cannot tell which message their handler died on.
        """
        harness = await self.make_harness()

        def on_chat(scene, chatmsg, msg):
            raise RuntimeError("handler blew up")

        harness.scene.on_chat_callback = on_chat

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            harness.inject_message(
                chat_topic("ctrl_uid"),
                {"object_id": "ctrl_uid", "type": "chat-ctrl", "text": "the-provoking-text"},
            )
            await harness.run_step(0.2)

        reported = stderr.getvalue()
        self.assertIn("the-provoking-text", reported)
        self.assertIn("handler blew up", reported)

    async def test_the_failing_object_payload_is_reported(self):
        """The object branch reports identically, through the same helper.

        Both branches route through _report_dispatch_error precisely so a user
        gets the same evidence whichever dispatch failed, so pin it on both.
        """
        harness = await self.make_harness()

        def on_msg(scene, obj, msg):
            raise RuntimeError("object handler blew up")

        harness.scene.on_msg_callback = on_msg

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            harness.inject_message(
                object_topic("reported_box"),
                {
                    "object_id": "reported_box",
                    "action": "create",
                    "type": "object",
                    "data": {"object_type": "box", "marker-of-this-payload": True},
                },
            )
            await harness.run_step(0.2)

        reported = stderr.getvalue()
        self.assertIn("marker-of-this-payload", reported)
        self.assertIn("object handler blew up", reported)

    async def test_a_base_exception_is_not_swallowed_by_the_guard(self):
        """The guard catches Exception, deliberately not BaseException.

        KeyboardInterrupt and SystemExit are not handler bugs to be logged and
        stepped over: a dispatch guard that ate a Ctrl-C would make the program
        unstoppable from the terminal. So for a BaseException the loop is
        *expected* to end, with no dispatch report -- which is what separates
        the `except Exception` written here from a wider `except BaseException`
        that would keep going and report.

        The exception raised is a plain BaseException subclass rather than a real
        KeyboardInterrupt: asyncio re-raises those two out of the event loop
        itself, which would take the test runner down with it and prove nothing
        about the guard.
        """
        harness = await self.make_harness()
        receive_loop = receive_loop_task(harness.scene)

        def on_chat(scene, chatmsg, msg):
            raise _BaseExc("not a handler bug")

        harness.scene.on_chat_callback = on_chat

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            await self.inject_chat(harness, "interrupt me")
            handled = []
            harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)
            await self.inject_chat(harness, "never seen", uuid="later_uid")

        self.assertEqual(handled, [])
        self.assertEqual(harness.scene.msg_queue.qsize(), 1)
        self.assertNotIn("Exception occured when processing payload", stderr.getvalue())
        # the receive loop's task is the one that died, carrying the raised
        # BaseException. Retrieving it also keeps asyncio from reporting it as
        # never retrieved when the task is collected.
        self.assertTrue(receive_loop.done())
        self.assertFalse(receive_loop.cancelled())
        self.assertIsInstance(receive_loop.exception(), _BaseExc)

    async def test_non_object_payload_does_not_stop_the_loop(self):
        """A bare JSON array on a scene topic is skipped, not fatal.

        json.loads accepts any JSON value, and the topic assignment that follows
        it -- payload["topic"] = msg.topic -- sits outside every try, so a bare
        array raised TypeError there and ended the receive loop for the rest of
        the session, past both dispatch guards. #257 sanctions closing this at
        the parsing boundary, so a payload that is not a JSON object is reported
        and skipped like an unparseable one.
        """
        harness = await self.make_harness()
        handled = []
        harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            harness.inject_message(chat_topic("bad_uid"), [1, 2, 3])
            await harness.run_step(0.2)
            await self.inject_chat(harness, "hello")

        self.assertEqual(handled, ["hello"])
        self.assertEqual(harness.scene.msg_queue.qsize(), 0)
        self.assertIn("non-object payload", stdout.getvalue())

    async def test_undecodable_payload_does_not_stop_the_loop(self):
        """A payload whose decode raises is reported and skipped, not fatal.

        The malformed-payload handler interpolates payload_str, which is
        assigned inside the try it guards. So when the *decode* is what raised,
        the handler itself raises UnboundLocalError, which escapes both try
        blocks and ends the task draining msg_queue for the rest of the session
        -- the same permanent failure the dispatch guards above exist to close,
        reached one line earlier and past all of them.

        Not reachable from a real broker today: paho always delivers bytes and
        bytes.decode("utf-8", "ignore") cannot raise. It is reachable from a
        test double or a future transport, which is what this test uses -- a str
        payload handed straight to MockMQTTTransport.mock_receive, since
        ArenaE2ETest.inject_message always encodes to bytes.
        """
        harness = await self.make_harness()
        handled = []
        harness.scene.on_chat_callback = lambda scene, chatmsg, msg: handled.append(chatmsg.text)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            # a str has no .decode, so the decode inside the try raises
            harness.transport.mock_receive(chat_topic("bad_uid"), "not-bytes")
            await harness.run_step(0.2)
            await self.inject_chat(harness, "hello")

        # asserted first, and by name, because it is the defect: the receive
        # loop dies with the handler's own UnboundLocalError, and AsyncWorker.run
        # prints that traceback to stdout on its way out.
        reported = stdout.getvalue()
        self.assertNotIn("UnboundLocalError", reported)
        self.assertEqual(handled, ["hello"])
        self.assertEqual(harness.scene.msg_queue.qsize(), 0)
        # the report has to name the payload it choked on, not the previous
        # message's payload and not nothing at all
        self.assertIn("Malformed payload", reported)
        self.assertIn("not-bytes", reported)

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
