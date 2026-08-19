"""Tests the span event recorded for a clientEvent nobody handled.

Scene._process_message records a span event for every clientEvent that reaches
the end of its branch -- one whose target is not in all_objects, or whose target
carries no evt_handler, since the branch above continues when it calls one. That
line was written as a plain string containing "{event}", so it recorded the
literal braces and never interpolated the event. The clientEvent branch was then
the one inbound path whose span said nothing about what had been handled, which
is the path you most want detail on when tracing an event that never reached its
handler.

ArenaTelemetry is a stub here (the OpenTelemetry implementation lives on the
telemetry branch) and its add_event is a no-op, so these tests record the calls
by replacing add_event on the scene's telemetry instance. start_span and
start_process_msg_span both return the telemetry object itself, so the "span"
_process_message adds events to is that same instance.
"""

import unittest

from arena.objects import Box, Object
from arena.test_system import ArenaE2ETest

CLIENT_EVENT_PREFIX = "Client event: "


class ClientEventSpanTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    async def make_harness(self):
        """Starts the harness and records every span event added to it.

        MockMQTTTransport fires on_connect on the event loop, and inject_message
        is silently dropped until the subscriptions it sets up exist.
        """
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        events = []
        harness.scene.telemetry.add_event = (
            lambda name, span=None, print_msg=True, **kwargs: events.append(name)
        )
        harness._start_tasks()
        for _ in range(10):
            if harness.transport.subscriptions:
                break
            await harness.run_step(0.1)
        return harness, events

    @staticmethod
    async def inject_client_event(harness, target, event_id="test_client"):
        """Injects a clientEvent aimed at target, as the inbound handler sees it.

        Scene._process_message drops any scene message whose payload object_id
        disagrees with the topic's uuid token, so the two have to match.
        """
        harness.inject_message(
            f"realm/s/user/test_scene/o/other_client/{event_id}",
            {
                "object_id": event_id,
                "action": "clientEvent",
                "type": "mousedown",
                "data": {"target": target, "targetPosition": {"x": 0, "y": 0, "z": 0}},
            },
        )
        await harness.run_step(0.2)

    @staticmethod
    def client_event_spans(events):
        return [name for name in events if name.startswith(CLIENT_EVENT_PREFIX)]

    async def test_span_recorded_for_unknown_target(self):
        """The branch under test is reached at all, so the rest can be asserted."""
        harness, events = await self.make_harness()

        await self.inject_client_event(harness, "no_such_object")

        self.assertEqual(len(self.client_event_spans(events)), 1)

    async def test_span_does_not_record_literal_braces(self):
        """The regression itself: an uninterpolated f-string placeholder."""
        harness, events = await self.make_harness()

        await self.inject_client_event(harness, "no_such_object")

        recorded = self.client_event_spans(events)[0]
        self.assertNotIn("{event}", recorded)
        self.assertNotIn("{", recorded)

    async def test_span_identifies_the_event(self):
        """The span has to carry something identifying what was handled.

        The target id is what a trace is read for here: it is the object the
        event was aimed at and did not reach.
        """
        harness, events = await self.make_harness()

        await self.inject_client_event(harness, "no_such_object")

        recorded = self.client_event_spans(events)[0]
        self.assertIn("no_such_object", recorded)
        self.assertIn("mousedown", recorded)

    async def test_span_recorded_for_known_target_without_handler(self):
        """The other way into this branch: target resolves, but has no handler."""
        harness, events = await self.make_harness()
        box = Box(object_id="quiet_box", position=(0, 0, 0), clickable=True)
        harness.scene.add_object(box)

        await self.inject_client_event(harness, "quiet_box")

        recorded = self.client_event_spans(events)
        self.assertEqual(len(recorded), 1)
        self.assertNotIn("{event}", recorded[0])
        self.assertIn("quiet_box", recorded[0])

    async def test_no_span_when_a_handler_ran(self):
        """A handled event continues before this line, so it records nothing here."""
        harness, events = await self.make_harness()
        box = Box(object_id="click_box", position=(0, 0, 0), clickable=True)
        box.evt_handler = lambda scene, evt, msg: None
        harness.scene.add_object(box)

        await self.inject_client_event(harness, "click_box")

        self.assertEqual(self.client_event_spans(events), [])

    async def test_distinct_events_record_distinct_spans(self):
        """Interpolation, not a fixed label: two events must not read the same.

        A literal string is identical for every event, which is exactly what
        makes it useless in a trace.
        """
        harness, events = await self.make_harness()

        await self.inject_client_event(harness, "target_one", event_id="client_one")
        await self.inject_client_event(harness, "target_two", event_id="client_two")

        recorded = self.client_event_spans(events)
        self.assertEqual(len(recorded), 2)
        self.assertNotEqual(recorded[0], recorded[1])


if __name__ == "__main__":
    unittest.main()
