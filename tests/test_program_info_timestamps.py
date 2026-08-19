"""Tests for the timestamp format of the program run-info fields.

ProgramRunInfo carries four timestamps -- create_time, last_active_time,
last_rcv_time and last_pub_time -- and all four reach the wire: the periodic
stats update calls Scene.run_info_update, which folds them into the program
object's data and publishes it on the scene-program topic. Consumers parse them,
so the format is a contract, not an internal detail.

That contract is `%Y-%m-%dT%H:%M:%S.%fZ` with millisecond precision, e.g.
"2025-12-16T22:11:11.001Z" -- the shape recorded in tests/trace_random_sphere.json
and the TIME_FMT that examples/legacy/localization/gt-sync.py parses with.

The failure these tests pin is a value carrying *both* a numeric UTC offset and a
trailing "Z" ("2026-08-19T02:04:18.826273+00Z"), which no parser accepts: a
timestamp is offset-qualified or Zulu, never both. So the assertion helper below
is deliberately strict about the whole shape, and ProgramInfoTimestampGuardTest
feeds it a known-bad value to prove it is strict enough to catch this -- a check
loose enough to accept "+00Z" would make every other test here vacuous.
"""

import json
import re
import unittest
from datetime import UTC, datetime

from arena.objects import Object
from arena.test_system import ArenaE2ETest
from arena.utils import ProgramRunInfo

# The format consumers parse these fields with.
TIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"

# strptime's %f accepts one to six fractional digits and Python's own
# fromisoformat accepts a numeric offset, so neither alone pins the contract.
# This pins it: exactly three fractional digits, a literal "Z", and no offset.
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

# The four run-info fields that reach the wire.
TIME_FIELDS = ("create_time", "last_active_time", "last_rcv_time", "last_pub_time")


def old_timestamp():
    """The pre-fix expression, kept as the negative control's input.

    datetime.now(UTC).isoformat() ends in the offset "+00:00", so slicing three
    characters off the end trims the offset rather than the microseconds, and
    appending "Z" leaves both an offset and a Zulu suffix:
    "2026-08-19T02:04:18.826273+00Z".
    """
    return datetime.now(UTC).isoformat()[:-3] + "Z"


class TimestampAssertion:
    """Mixin: the strict check shared by every case in this module."""

    def assert_arena_timestamp(self, value, field):
        self.assertIsInstance(value, str, f"{field} should be a string, got {value!r}")
        self.assertRegex(
            value,
            TIME_RE,
            f"{field} must be UTC with millisecond precision and a Zulu suffix "
            f"and no numeric offset, got {value!r}",
        )
        try:
            datetime.strptime(value, TIME_FMT)
        except ValueError as e:
            self.fail(f"{field} does not parse with {TIME_FMT!r}: {value!r} ({e})")


class ProgramInfoTimestampGuardTest(TimestampAssertion, unittest.TestCase):
    """Negative control: the assertion helper must reject the pre-fix output.

    Without this, a helper loose enough to accept "+00Z" would let every other
    test in this module pass against the bug it is meant to catch.
    """

    def test_helper_rejects_old_offset_plus_z_expression(self):
        bad = old_timestamp()
        self.assertIn("+00Z", bad, f"expected the pre-fix shape, got {bad!r}")
        with self.assertRaises(self.failureException):
            self.assert_arena_timestamp(bad, "old_expression")

    def test_helper_rejects_microsecond_precision(self):
        """Six fractional digits are not the millisecond contract."""
        with self.assertRaises(self.failureException):
            self.assert_arena_timestamp("2026-08-19T02:04:18.826273Z", "microseconds")

    def test_helper_rejects_bare_offset_without_z(self):
        with self.assertRaises(self.failureException):
            self.assert_arena_timestamp("2026-08-19T02:04:18.826+00:00", "offset")

    def test_helper_accepts_the_contract_shape(self):
        """The shape recorded in tests/trace_random_sphere.json."""
        self.assert_arena_timestamp("2025-12-16T22:11:11.001Z", "contract")


class ProgramRunInfoTimestampTest(TimestampAssertion, unittest.TestCase):
    """ProgramRunInfo sets all four fields in the contract format."""

    def test_create_and_last_active_time_on_construction(self):
        info = ProgramRunInfo()
        for field in ("create_time", "last_active_time"):
            self.assert_arena_timestamp(getattr(info, field), field)

    def test_msg_rcv_sets_rcv_and_active_times(self):
        info = ProgramRunInfo()
        info.msg_rcv()
        for field in ("last_rcv_time", "last_active_time"):
            self.assert_arena_timestamp(getattr(info, field), field)

    def test_msg_publish_sets_pub_and_active_times(self):
        info = ProgramRunInfo()
        info.msg_publish()
        for field in ("last_pub_time", "last_active_time"):
            self.assert_arena_timestamp(getattr(info, field), field)

    def test_all_four_fields_after_a_receive_and_a_publish(self):
        info = ProgramRunInfo()
        info.msg_rcv()
        info.msg_publish()
        for field in TIME_FIELDS:
            self.assert_arena_timestamp(getattr(info, field), field)


class SceneProgramInfoTimestampTest(TimestampAssertion, unittest.IsolatedAsyncioTestCase):
    """The same four fields, driven through a real Scene and onto the wire."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    async def make_connected_harness(self):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        harness._start_tasks()
        for _ in range(10):  # subscriptions are set up by the connect task
            if harness.transport.subscriptions:
                break
            await harness.run_step(0.1)
        return harness

    async def test_fields_parse_after_a_real_receive_and_publish(self):
        """A received message and a published object go through the real hooks.

        Scene.on_message calls run_info.msg_rcv(), and the mock transport's
        publish() invokes Scene.on_publish, which calls run_info.msg_publish() --
        so this exercises the receive and publish paths, not the setters alone.
        """
        harness = await self.make_connected_harness()
        scene = harness.scene

        harness.inject_message(
            "realm/s/user/test_scene/o/other_client/ts_probe",
            {
                "object_id": "ts_probe",
                "action": "create",
                "type": "object",
                "data": {"object_type": "box"},
            },
        )
        await harness.run_step(0.1)

        scene.add_object(Object(object_id="ts_published", object_type="box"))
        await harness.run_step(0.1)

        run_info = scene.run_info
        for field in TIME_FIELDS:
            value = getattr(run_info, field)
            self.assertIsNotNone(value, f"{field} was never set; the path did not run")
            self.assert_arena_timestamp(value, field)

    async def test_fields_parse_in_the_published_program_payload(self):
        """The values as a consumer of the scene-program topic actually sees them."""
        harness = await self.make_connected_harness()
        scene = harness.scene

        harness.inject_message(
            "realm/s/user/test_scene/o/other_client/ts_probe2",
            {
                "object_id": "ts_probe2",
                "action": "create",
                "type": "object",
                "data": {"object_type": "box"},
            },
        )
        await harness.run_step(0.1)
        scene.add_object(Object(object_id="ts_published2", object_type="box"))
        await harness.run_step(0.1)

        # Publish the program object the way the periodic stats update does.
        scene.run_info_update(scene.run_info)
        await harness.run_step(0.1)

        payloads = [
            json.loads(m["payload"])
            for m in harness.capture_published_messages()
            if "/p/" in m["topic"] or "program" in m["topic"]
        ]
        run_infos = [
            p["data"][ProgramRunInfo.object_type]
            for p in payloads
            if isinstance(p.get("data"), dict)
            and ProgramRunInfo.object_type in p["data"]
        ]
        self.assertTrue(run_infos, "no published program payload carried run_info")

        for run_info in run_infos:
            for field in TIME_FIELDS:
                self.assertIn(field, run_info, f"{field} missing from published run_info")
                self.assert_arena_timestamp(run_info[field], f"published {field}")


if __name__ == "__main__":
    unittest.main()
