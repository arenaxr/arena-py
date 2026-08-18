"""Tests for the scene object reference handed to evt_handler callbacks.

An inbound clientEvent names its target by object_id, and Scene._process_message
already looks that id up in all_objects to find the handler to call. These tests
pin that the resolved object travels to the handler as event.object, so handlers
do not have to repeat the lookup.

They also pin the serialization side of that, which is the part that can bite:
Event.json() builds its payload from vars(self), so a live Object hung off an
Event would otherwise ride out onto the wire -- leaking the private handler and
task state that Object.json_preprocess exists to strip, and outright raising
"Circular reference detected" for a hand or camera target, whose obj.camera /
user.hands links form a real cycle (see Scene._process_message).

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite.
"""

import json
import unittest

from arena.attributes import Position
from arena.events import Event
from arena.objects import Box, Camera, HandLeft, Object
from arena.test_system import ArenaE2ETest


def make_camera(object_id="camera_test_test"):
    """Builds a Camera the way Scene does, from a data dict.

    Camera.__init__ only calls super().__init__ when data carries a position or
    rotation, so the position here is what makes it a usable object.
    """
    return Camera(object_id=object_id, data={"position": {"x": 0, "y": 1.6, "z": 0}})


def make_linked_hand(camera, object_id="handLeft_test_test"):
    """Builds a hand joined to camera exactly as Scene._process_message joins them.

    That pairing (user.hands[object_type] = obj; obj.camera = user) is a genuine
    reference cycle, which is why it belongs in these tests.
    """
    hand = HandLeft(
        object_id=object_id,
        data={"position": {"x": 0, "y": 1, "z": 0}, "dep": camera.object_id},
    )
    camera.hands[hand.object_type] = hand
    hand.camera = camera
    return hand


class EventObjectRefTestCase(unittest.TestCase):
    """Event.object is local-only state and must never reach the wire."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make_event(target):
        """Builds a clientEvent the way Scene.generate_click_event does.

        targetPosition, not position: DataEvent.position is a deprecated
        property whose getter returns None, so it would not read back.
        """
        return Event(
            object_id="test_client",
            type="mousedown",
            target=target,
            targetPosition=Position(0, 0, 0),
        )

    def test_event_object_defaults_to_none(self):
        """An Event nobody resolved a target for still answers .object, with None.

        Events built by generate_click_event / generate_custom_event never go
        through the inbound lookup, so handlers need a defined answer rather than
        an AttributeError.
        """
        event = self.make_event("some_box")
        self.assertIsNone(event.object)

    def test_object_is_an_instance_attribute(self):
        """object lives on the instance, not on the class.

        A class-level default would read the same through evt.object but would
        make "object" in evt and vars(evt) disagree with every other Event
        field, and Event.json() builds its payload out of vars(self).
        """
        event = self.make_event("some_box")

        self.assertIn("object", vars(event))
        self.assertIn("object", event)
        self.assertNotIn("object", vars(type(event)))

    def test_json_omits_object_reference(self):
        """The wire payload carries the target id, never the object itself."""
        box = Box(object_id="ref_box", position=(1, 2, 3))
        event = self.make_event("ref_box")
        event.object = box

        payload = json.loads(event.json())

        self.assertNotIn("object", payload)
        self.assertEqual(payload["data"]["target"], "ref_box")

    def test_json_omits_object_reference_when_none(self):
        """The default None is dropped too, so unresolved events keep their shape."""
        payload = json.loads(self.make_event("ref_box").json())

        self.assertNotIn("object", payload)

    def test_json_does_not_leak_private_object_state(self):
        """Attaching an object must not smuggle Object's skipped keys onto the wire.

        These are the keys Object.json_preprocess strips: callables and asyncio
        tasks that are neither JSON-encodable nor any of the server's business.
        """
        box = Box(object_id="ref_box", position=(1, 2, 3))
        box.evt_handler = lambda scene, evt, msg: None
        event = self.make_event("ref_box")
        event.object = box

        wire = event.json()

        for private_key in (
            "evt_handler",
            "update_handler",
            "animations",
            "delayed_prop_tasks",
        ):
            self.assertNotIn(private_key, wire)

    def test_json_size_is_unchanged_by_object_reference(self):
        """Byte-for-byte identical with and without the reference attached."""
        box = Box(object_id="ref_box", position=(1, 2, 3))
        without = self.make_event("ref_box").json()

        event = self.make_event("ref_box")
        event.object = box
        with_ref = event.json()

        self.assertEqual(with_ref, without)

    def test_json_with_hand_target_does_not_raise(self):
        """A hand's obj.camera.hands cycle would make json.dumps raise."""
        hand = make_linked_hand(make_camera())
        event = self.make_event(hand.object_id)
        event.object = hand

        payload = json.loads(event.json())  # must not raise ValueError

        self.assertNotIn("object", payload)

    def test_json_with_camera_target_does_not_raise(self):
        """Same cycle, reached from the camera side."""
        camera = make_camera()
        make_linked_hand(camera)
        event = self.make_event(camera.object_id)
        event.object = camera

        payload = json.loads(event.json())  # must not raise ValueError

        self.assertNotIn("object", payload)

    def test_json_other_kwargs_still_merge(self):
        """Filtering object out must not disturb the kwargs callers do pass.

        Scene._publish calls json(action=..., timestamp=...), so those have to
        survive the filter.
        """
        event = self.make_event("ref_box")

        payload = json.loads(event.json(action="clientEvent", timestamp="t"))

        self.assertEqual(payload["action"], "clientEvent")
        self.assertEqual(payload["timestamp"], "t")

    def test_json_object_kwarg_cannot_reintroduce_object(self):
        """A caller passing object= into json() cannot put it on the wire.

        json() merges **kwargs into the payload, so the filter has to run after
        that merge, not before it. Filtered first, this kwarg walks straight
        back in and leaks the private state below.
        """
        box = Box(object_id="ref_box", position=(1, 2, 3))
        box.evt_handler = lambda scene, evt, msg: None
        event = self.make_event("ref_box")

        wire = event.json(object=box)

        self.assertNotIn("object", json.loads(wire))
        for private_key in (
            "evt_handler",
            "update_handler",
            "animations",
            "delayed_prop_tasks",
        ):
            self.assertNotIn(private_key, wire)

    def test_json_object_kwarg_with_hand_does_not_raise(self):
        """Same kwarg, with the cycle: reintroducing a hand would raise.

        Filtered before the merge this is not bloat but a hard
        ValueError: Circular reference detected out of json.dumps.
        """
        hand = make_linked_hand(make_camera())
        event = self.make_event(hand.object_id)

        payload = json.loads(event.json(object=hand))  # must not raise

        self.assertNotIn("object", payload)

    def test_constructor_object_kwarg_sets_the_attribute(self):
        """Event(object=obj) has to reach the attribute it names.

        Unconsumed, "object" falls through into DataEvent, which has no
        Object-rejection guard, so it lands in data instead of on the Event.
        """
        box = Box(object_id="ref_box", position=(1, 2, 3))

        event = Event(
            object_id="test_client",
            type="mousedown",
            target="ref_box",
            object=box,
        )

        self.assertIs(event.object, box)
        self.assertNotIn("object", vars(event.data))

    def test_constructor_object_kwarg_stays_off_the_wire(self):
        """...and having reached the attribute, it is filtered like any other.

        Left in data it would ride out nested under "data", carrying the same
        private state the top-level filter exists to strip.
        """
        box = Box(object_id="ref_box", position=(1, 2, 3))
        box.evt_handler = lambda scene, evt, msg: None

        wire = Event(
            object_id="test_client",
            type="mousedown",
            target="ref_box",
            object=box,
        ).json()

        payload = json.loads(wire)
        self.assertNotIn("object", payload)
        self.assertNotIn("object", payload["data"])
        for private_key in (
            "evt_handler",
            "update_handler",
            "animations",
            "delayed_prop_tasks",
        ):
            self.assertNotIn(private_key, wire)

    def test_constructor_object_kwarg_with_data_dict_sets_the_attribute(self):
        """The data-dict shape must not discard the object silently.

        Event.__init__ replaces kwargs with kwargs["data"] when a data dict is
        given, so an unconsumed "object" is dropped outright, with no error.
        """
        box = Box(object_id="ref_box", position=(1, 2, 3))

        event = Event(
            object_id="test_client",
            type="mousedown",
            data={"target": "ref_box"},
            object=box,
        )

        self.assertIs(event.object, box)
        self.assertEqual(event.data.target, "ref_box")
        self.assertNotIn("object", json.loads(event.json()))


class SceneEvtHandlerObjectRefTestCase(unittest.IsolatedAsyncioTestCase):
    """The inbound clientEvent path hands its resolved object to the handler."""

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
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        harness._start_tasks()
        for _ in range(10):
            if harness.transport.subscriptions:
                break
            await harness.run_step(0.1)
        return harness

    @staticmethod
    async def inject_client_event(harness, target, event_id="test_client"):
        """Injects a clientEvent aimed at target, as the inbound handler sees it.

        Scene._process_message drops any scene message whose payload object_id
        disagrees with the topic's uuid token, so the two must match.
        """
        harness.inject_message(
            f"realm/s/user/test_scene/o/other_client/{event_id}",
            {
                "object_id": event_id,
                "action": "clientEvent",
                "type": "mousedown",
                "data": {
                    "target": target,
                    # targetPosition, not the deprecated position: this is the
                    # spelling that reads back off the DataEvent
                    "targetPosition": {"x": 0, "y": 0, "z": 0},
                },
            },
        )
        await harness.run_step(0.2)

    async def test_handler_receives_object_reference(self):
        """The handler gets the very object it was registered on, not a copy."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        received = []
        box.evt_handler = lambda scene, evt, msg: received.append(evt)
        harness.scene.add_object(box)

        await self.inject_client_event(harness, "click_box")

        self.assertEqual(len(received), 1)
        self.assertIs(received[0].object, box)

    async def test_handler_object_reference_is_live(self):
        """It is the live scene object, so reads through it see current state."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(1, 2, 3), clickable=True)
        seen = []
        box.evt_handler = lambda scene, evt, msg: seen.append(evt.object.data.position)
        harness.scene.add_object(box)

        await self.inject_client_event(harness, "click_box")

        self.assertEqual(len(seen), 1)
        self.assertIs(seen[0], box.data.position)

    async def test_handler_event_still_carries_target_id(self):
        """The reference is additive: the event's own fields keep working."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        received = []
        box.evt_handler = lambda scene, evt, msg: received.append(evt)
        harness.scene.add_object(box)

        await self.inject_client_event(harness, "click_box")

        self.assertEqual(received[0].data.target, "click_box")
        self.assertEqual(received[0].object_id, "test_client")
        self.assertEqual(received[0].type, "mousedown")
        # reads back, unlike the deprecated data.position whose getter is None
        self.assertEqual(vars(received[0].data.targetPosition)["x"], 0)

    async def test_handler_may_republish_its_event(self):
        """A handler that re-emits the event it was handed must not break.

        This is the regression that motivated filtering Event.json(): the
        reference is attached by the library, so a handler can reach
        generate_custom_event with it still in place without knowing.
        """
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        box.evt_handler = lambda scene, evt, msg: scene.generate_custom_event(evt)
        harness.scene.add_object(box)
        before = len(harness.capture_published_messages())

        await self.inject_client_event(harness, "click_box")

        published = harness.capture_published_messages()[before:]
        echoed = [
            json.loads(m["payload"])
            for m in published
            if json.loads(m["payload"]).get("action") == "clientEvent"
        ]
        self.assertEqual(len(echoed), 1)
        self.assertNotIn("object", echoed[0])

    async def test_hand_handler_may_republish_its_event(self):
        """Same, for the hand target whose reference cycle used to raise."""
        harness = await self.make_harness()
        camera = make_camera()
        hand = make_linked_hand(camera)
        hand.evt_handler = lambda scene, evt, msg: scene.generate_custom_event(evt)
        # constructing the hand already registered it in all_objects; it is not
        # published, because a client never re-publishes a server-owned hand
        self.assertIn(hand.object_id, harness.scene.all_objects)
        before = len(harness.capture_published_messages())

        await self.inject_client_event(harness, hand.object_id)

        published = harness.capture_published_messages()[before:]
        echoed = [
            json.loads(m["payload"])
            for m in published
            if json.loads(m["payload"]).get("action") == "clientEvent"
        ]
        self.assertEqual(len(echoed), 1)
        self.assertNotIn("object", echoed[0])

    async def test_generate_click_event_object_kwarg_stays_off_the_wire(self):
        """The public path that forwards **kwargs into Event.__init__.

        generate_click_event passes its **kwargs straight through, so object=
        is the natural thing to write once event.object is documented. It has
        to reach the attribute, and stay off the wire.
        """
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(1, 2, 3), clickable=True)
        box.evt_handler = lambda scene, evt, msg: None
        harness.scene.add_object(box)
        before = len(harness.capture_published_messages())

        harness.scene.generate_click_event(box, object=box)
        await harness.run_step(0.2)

        published = harness.capture_published_messages()[before:]
        echoed = [
            json.loads(m["payload"])
            for m in published
            if json.loads(m["payload"]).get("action") == "clientEvent"
        ]
        self.assertEqual(len(echoed), 1)
        self.assertNotIn("object", echoed[0])
        self.assertNotIn("object", echoed[0]["data"])
        self.assertNotIn("evt_handler", json.dumps(echoed[0]))

    async def test_unknown_target_leaves_object_none(self):
        """An event for an object this client does not know keeps object None.

        No handler can fire for an unknown target today, so this is asserted on
        the Event the general on_msg_callback receives.
        """
        harness = await self.make_harness()
        received = []
        harness.scene.on_msg_callback = lambda scene, evt, msg: received.append(evt)

        await self.inject_client_event(harness, "no_such_object")

        events = [e for e in received if isinstance(e, Event)]
        self.assertEqual(len(events), 1)
        self.assertIsNone(events[0].object)

    async def test_known_target_without_handler_still_resolves_object(self):
        """The lookup succeeded, so the reference is set even with no evt_handler."""
        harness = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        harness.scene.add_object(box)
        received = []
        harness.scene.on_msg_callback = lambda scene, evt, msg: received.append(evt)

        await self.inject_client_event(harness, "click_box")

        events = [e for e in received if isinstance(e, Event)]
        self.assertEqual(len(events), 1)
        self.assertIs(events[0].object, box)


if __name__ == "__main__":
    unittest.main()
