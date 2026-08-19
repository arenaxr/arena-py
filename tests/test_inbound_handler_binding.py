"""Tests that an inbound message cannot install or replace an object's handlers.

evt_handler and update_handler are local-only fields: Object.json_preprocess
strips them on the way out, so they never legitimately appear on the wire in
either direction. But Object.__init__ and Object.update_attributes both take
them as named parameters, and Scene.process_message reaches both with the raw
inbound payload -- ObjClass(**payload) and obj.update_attributes(**payload). So
a top-level "evt_handler" in a create or update message used to bind, on any
object this client knows.

The trust consequence is the point: a remote sender could replace the handler on
an object this program owns, and the object then went quiet. Nothing about it
distinguished it from an object whose handler was never registered -- the
substitute is not callable, so every later clientEvent for it died inside
callback_wrapper's signature() call, caught by the broad guard in
process_message and logged, with the handler left replaced for the life of the
process.

The fix is at the parsing boundary and is a rejection, not a repair: a handler
is kept only when it is callable, which json.loads can never produce, so a
sender's value is discarded rather than coerced or stored. It is the same
discriminator Event.__init__ uses for its "object" field (see #246).

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite.
"""

import unittest

from arena.objects import Box, Object
from arena.test_system import ArenaE2ETest
from arena.topics import PUBLISH_TOPICS

SCENE = "test_scene"
NAMESPACE = "user"
REALM = "realm"


def object_topic(object_id, user_client="other_client"):
    """Topic for an inbound scene object message from another client.

    The objectId token has to equal the payload's object_id, or
    Scene.process_message discards the message before any dispatch.
    """
    return PUBLISH_TOPICS.SCENE_OBJECTS.substitute(
        realm=REALM, nameSpace=NAMESPACE, sceneName=SCENE, userClient=user_client, objectId=object_id
    )


class HandlerParameterTestCase(unittest.TestCase):
    """The Object API keeps a handler only when it is callable."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def test_constructor_keeps_a_callable_handler(self):
        """The ordinary local case is untouched."""

        def handler(scene, evt, msg):
            pass

        box = Box(object_id="click_box", evt_handler=handler, update_handler=handler)

        self.assertIs(box.evt_handler, handler)
        self.assertIs(box.update_handler, handler)

    def test_constructor_rejects_a_string_handler(self):
        """A string is what a remote sender actually gets to send.

        Object(**payload) is how Scene.process_message builds an object it has
        not seen before, straight from the inbound payload.
        """
        box = Box(object_id="click_box", evt_handler="PWNED", update_handler="PWNED")

        self.assertIsNone(box.evt_handler)
        self.assertIsNone(box.update_handler)

    def test_constructor_rejects_structured_handlers(self):
        """Every other shape json.loads can produce is rejected too.

        None is not a rejection, it is the documented default, so it keeps
        reading back as None either way.
        """
        for value in ("PWNED", 1, 0, True, [], ["a"], {}, {"call": "me"}, 1.5):
            with self.subTest(value=value):
                box = Box(object_id="click_box", evt_handler=value)
                self.assertIsNone(box.evt_handler)

    def test_rejected_handler_is_not_diverted_into_data(self):
        """Rejecting the value must not push it somewhere else instead.

        __init__ consumes the named parameter, so a rejected value has to be
        dropped, not fall through into the object's data and out onto the wire.
        """
        box = Box(object_id="click_box", evt_handler="PWNED")

        self.assertNotIn("evt_handler", vars(box.data))
        self.assertNotIn("PWNED", box.json())

    def test_update_attributes_keeps_a_callable_handler(self):
        """Local code may still (re)bind a handler through update_attributes."""

        def evt_handler(scene, evt, msg):
            pass

        def update_handler(obj):
            pass

        box = Box(object_id="click_box")
        box.update_attributes(evt_handler=evt_handler, update_handler=update_handler)

        self.assertIs(box.evt_handler, evt_handler)
        self.assertIs(box.update_handler, update_handler)

    def test_update_attributes_rejects_a_string_handler(self):
        """...and a non-callable leaves the existing handler in place.

        This is the exact reach of the bug: obj.update_attributes(**payload) for
        an object already in all_objects.
        """

        def evt_handler(scene, evt, msg):
            pass

        def update_handler(obj):
            pass

        box = Box(object_id="click_box", evt_handler=evt_handler, update_handler=update_handler)

        box.update_attributes(evt_handler="PWNED", update_handler="PWNED")

        self.assertIs(box.evt_handler, evt_handler)
        self.assertIs(box.update_handler, update_handler)

    def test_update_attributes_with_no_handler_leaves_it_alone(self):
        """Omitting the field is not the same as clearing it.

        Almost every inbound update carries no handler field at all, so this is
        the common path, and the guard must not disturb it.
        """

        def handler(scene, evt, msg):
            pass

        box = Box(object_id="click_box", evt_handler=handler)

        box.update_attributes(position={"x": 1, "y": 2, "z": 3})

        self.assertIs(box.evt_handler, handler)

    def test_rejected_update_handler_is_not_invoked(self):
        """update_attributes calls update_handler at the end of the same call.

        Bound, a string handler raised TypeError right there, aborting the rest
        of that message's processing -- so this is not only about the next event.
        """
        box = Box(object_id="click_box")

        # must not raise
        box.update_attributes(update_handler="PWNED", position={"x": 1, "y": 2, "z": 3})

        self.assertIsNone(box.update_handler)
        self.assertEqual(vars(box.data.position)["x"], 1)


class InboundHandlerBindingTestCase(unittest.IsolatedAsyncioTestCase):
    """The inbound object path is a trust boundary for these two fields."""

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
    async def inject_object_message(harness, object_id, action, data=None, payload_extras=None):
        """Injects a create/update aimed at object_id, as the inbound path sees it."""
        payload = {
            "object_id": object_id,
            "action": action,
            "type": "object",
            "data": data if data is not None else {},
        }
        if payload_extras:
            payload.update(payload_extras)
        harness.inject_message(object_topic(object_id), payload)
        await harness.run_step(0.2)

    @staticmethod
    async def inject_client_event(harness, target, event_id="evt_client"):
        """Injects a genuine clientEvent aimed at target."""
        harness.inject_message(
            object_topic(event_id),
            {
                "object_id": event_id,
                "action": "clientEvent",
                "type": "mousedown",
                "data": {"target": target, "targetPosition": {"x": 0, "y": 0, "z": 0}},
            },
        )
        await harness.run_step(0.2)

    async def test_update_cannot_replace_a_registered_evt_handler(self):
        """The handler this program registered is still the object's handler."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)

        def handler(scene, evt, msg):
            pass

        box.evt_handler = handler
        harness.scene.add_object(box)

        await self.inject_object_message(
            harness, "click_box", "update", payload_extras={"evt_handler": "PWNED"}
        )

        self.assertIs(harness.scene.all_objects["click_box"], box)
        self.assertIs(box.evt_handler, handler)

    async def test_object_keeps_firing_its_events_after_such_an_update(self):
        """The consequence a user would actually notice: the object stays live.

        Before the guard the substitute was bound and every later clientEvent
        for this object died in callback_wrapper, so the handler never ran again
        for the life of the process.
        """
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        fired = []
        box.evt_handler = lambda scene, evt, msg: fired.append(evt)
        harness.scene.add_object(box)

        await self.inject_object_message(
            harness, "click_box", "update", payload_extras={"evt_handler": "PWNED"}
        )
        for _ in range(3):
            await self.inject_client_event(harness, "click_box")

        self.assertEqual(len(fired), 3)

    async def test_the_rest_of_that_same_update_still_applies(self):
        """Only the handler field is rejected; the message is not discarded.

        A create or update carrying one of these names is still an ordinary
        scene message, and its genuine attributes have to land as they would
        have without it.
        """
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        box.evt_handler = lambda scene, evt, msg: None
        harness.scene.add_object(box)

        await self.inject_object_message(
            harness,
            "click_box",
            "update",
            data={"position": {"x": 9, "y": 9, "z": 9}},
            payload_extras={"evt_handler": "PWNED"},
        )

        self.assertEqual(vars(box.data.position)["x"], 9)

    async def test_create_cannot_install_an_evt_handler(self):
        """A brand-new object arrives with no handler, whatever the sender sent.

        This is the ObjClass(**payload) reach: the object did not exist locally,
        so there was nothing to overwrite -- the sender was installing.
        """
        harness = await self.make_harness()

        await self.inject_object_message(
            harness,
            "new_box",
            "create",
            data={"object_type": "box"},
            payload_extras={"evt_handler": "PWNED"},
        )

        self.assertIn("new_box", harness.scene.all_objects)
        self.assertIsNone(harness.scene.all_objects["new_box"].evt_handler)

    async def test_create_cannot_install_an_update_handler(self):
        """Same for update_handler, which update_attributes also *calls*."""
        harness = await self.make_harness()

        await self.inject_object_message(
            harness,
            "new_box",
            "create",
            data={"object_type": "box"},
            payload_extras={"update_handler": "PWNED"},
        )

        self.assertIn("new_box", harness.scene.all_objects)
        self.assertIsNone(harness.scene.all_objects["new_box"].update_handler)

    async def test_update_handler_in_a_create_does_not_abort_that_message(self):
        """A bound update_handler raised mid-message, so later callbacks were lost.

        update_attributes invokes it at the end of the same call, inside the
        object branch's try, so on_msg_callback and new_obj_callback never ran
        for that message.
        """
        harness = await self.make_harness()
        seen_msgs = []
        new_objs = []
        harness.scene.on_msg_callback = lambda scene, obj, msg: seen_msgs.append(obj)
        harness.scene.new_obj_callback = lambda scene, obj, msg: new_objs.append(obj)

        # no object_type: that is the payload shape new_obj_callback fires for,
        # so one message exercises both callbacks that used to be skipped
        await self.inject_object_message(
            harness, "new_box", "create", payload_extras={"update_handler": "PWNED"}
        )

        self.assertEqual(len(seen_msgs), 1)
        self.assertEqual(len(new_objs), 1)

    async def test_update_cannot_replace_a_registered_update_handler(self):
        """And on an object this program already owns, the real one survives."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0))
        updates = []
        box.update_handler = lambda obj: updates.append(obj)
        harness.scene.add_object(box)

        await self.inject_object_message(
            harness,
            "click_box",
            "update",
            data={"position": {"x": 4, "y": 4, "z": 4}},
            payload_extras={"update_handler": "PWNED"},
        )

        self.assertIs(harness.scene.all_objects["click_box"], box)
        self.assertEqual(len(updates), 1)
        self.assertIs(updates[0], box)

    async def test_object_shaped_handler_payloads_are_rejected_too(self):
        """A sender is not limited to strings; no JSON shape is accepted.

        Nothing json.loads can produce is callable, so the guard has no gap to
        aim at -- but the shapes worth naming are the ones that look plausible.
        """
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)

        def handler(scene, evt, msg):
            pass

        box.evt_handler = handler
        harness.scene.add_object(box)

        for value in ({"name": "handler"}, ["handler"], 42, True, "arena.objects.Object"):
            with self.subTest(value=value):
                await self.inject_object_message(
                    harness, "click_box", "update", payload_extras={"evt_handler": value}
                )
                self.assertIs(box.evt_handler, handler)


if __name__ == "__main__":
    unittest.main()
