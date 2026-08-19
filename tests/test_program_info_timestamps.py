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

Shape is not the whole contract, though: the "Z" claims UTC, so the helper also
checks the value really is a UTC instant. Without that, swapping the producer's
datetime.now(UTC) for datetime.now() keeps every shape assertion green while
shipping local time under a "Z".

That instant check is only as good as the clock it reads, and against a *live*
producer it compares two readings of the same machine clock -- so it detects a
naive-clock producer only when the runner's own zone is not UTC. The tests
workflow sets no TZ and GitHub runners are UTC, where such a producer bug is
invisible to a live-clock comparison. So the cases that must hold whatever zone
CI runs in do not rely on the runner's zone at all: they pin a fixed instant
whose UTC and local readings differ by a real offset --
ProgramRunInfoFixedClockTest for the producer, and the local-time-labelled-UTC
guard for the helper. The live-clock producer cases below stay as a smoke test
that the real code path runs, not as the zone check.
"""

import json
import re
import unittest
from datetime import UTC, datetime, timedelta, timezone

from unittest import mock

from arena.objects import Object
from arena.test_system import ArenaE2ETest
from arena.utils import ProgramRunInfo
from arena.utils import program_info

# The format consumers parse these fields with.
TIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"

# strptime's %f accepts one to six fractional digits and Python's own
# fromisoformat accepts a numeric offset, so neither alone pins the contract.
# This pins it: exactly three fractional digits, a literal "Z", and no offset.
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

# The four run-info fields that reach the wire.
TIME_FIELDS = ("create_time", "last_active_time", "last_rcv_time", "last_pub_time")

# How far a timestamp may sit from now(UTC) and still count as "this instant".
# Loose enough that a slow or heavily loaded CI runner can build the value minutes
# before the assertion reads it; far tighter than any real timezone offset, the
# smallest of which is 30 minutes, so a local-time reading cannot slip through.
MAX_CLOCK_SKEW = timedelta(minutes=5)

# A fixed instant, and a fixed zone four hours behind it. The producer under a
# fake clock pinned to both readings is checkable without consulting the runner's
# zone: whichever reading it takes is a known string, so TZ cannot make the two
# agree the way it does on a UTC runner.
FIXED_INSTANT = datetime(2026, 8, 19, 12, 0, 0, 1000, tzinfo=UTC)
FIXED_LOCAL_ZONE = timezone(timedelta(hours=-4))

# What the producer must emit under that clock: the UTC reading, to the ms.
FIXED_UTC_RENDERING = "2026-08-19T12:00:00.001Z"

# What a naive datetime.now() producer would emit instead -- same shape, same
# millisecond, four hours out. Named so a failure message can show the mistake.
FIXED_LOCAL_RENDERING = "2026-08-19T08:00:00.001Z"


class FixedNonUTCClock:
    """Stands in for the `datetime` the program_info module calls `now` on.

    `now(UTC)` yields FIXED_INSTANT; the bare `now()` that a naive producer would
    call yields the same instant read as a wall clock four hours behind, with the
    tzinfo dropped -- exactly what `datetime.now()` returns on a host in that
    zone. The gap between the two is baked into the fake, so it is there on a UTC
    runner too, which is the whole point: a producer that reads the wrong one is
    caught by the value it emits rather than by a skew against the local clock.
    """

    @staticmethod
    def now(tz=None):
        if tz is None:
            return FIXED_INSTANT.astimezone(FIXED_LOCAL_ZONE).replace(tzinfo=None)
        return FIXED_INSTANT.astimezone(tz)


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

    def assert_timestamp_shape(self, value, field):
        """Shape only: the contract format, nothing about which instant it names.

        Returns the naive datetime the contract format parses out, for callers
        that go on to check the instant.
        """
        self.assertIsInstance(value, str, f"{field} should be a string, got {value!r}")
        self.assertRegex(
            value,
            TIME_RE,
            f"{field} must be UTC with millisecond precision and a Zulu suffix "
            f"and no numeric offset, got {value!r}",
        )
        try:
            return datetime.strptime(value, TIME_FMT)
        except ValueError as e:
            self.fail(f"{field} does not parse with {TIME_FMT!r}: {value!r} ({e})")

    def assert_arena_timestamp(self, value, field):
        """The full contract: the right shape *and* the right instant.

        The shape alone does not pin the zone. Replace the producer's
        datetime.now(UTC) with datetime.now() and the trailing "Z" stays put, the
        regex still matches, strptime still parses -- and the value is local time
        wearing a UTC label, four hours out under TZ=America/New_York. So read the
        parsed value as UTC, which is what the "Z" promises a consumer, and require
        it to land within MAX_CLOCK_SKEW of now(UTC).
        """
        parsed = self.assert_timestamp_shape(value, field)
        skew = abs(datetime.now(UTC) - parsed.replace(tzinfo=UTC))
        self.assertLessEqual(
            skew,
            MAX_CLOCK_SKEW,
            f"{field} carries a Zulu suffix but read as UTC it is {skew} away from "
            f"now(UTC), so it is not the instant it claims to be -- a local clock "
            f"reading labelled UTC looks exactly like this: {value!r}",
        )


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

    def test_helper_rejects_a_local_time_reading_labelled_utc(self):
        """Right shape, wrong instant: what datetime.now() instead of now(UTC) emits.

        Built against a fixed -04:00 offset rather than the runner's own zone, so
        the case holds whatever TZ CI sets -- including UTC, where a producer bug
        of this kind would otherwise be invisible.
        """
        local = datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)
        value = f"{local.strftime('%Y-%m-%dT%H:%M:%S')}.{local.microsecond // 1000:03d}Z"
        self.assert_timestamp_shape(value, "local_time")  # the shape is fine
        with self.assertRaises(self.failureException):
            self.assert_arena_timestamp(value, "local_time")

    def test_helper_accepts_the_contract_shape(self):
        """The shape recorded in tests/trace_random_sphere.json.

        A recorded literal names a fixed instant in 2025, so this is the
        shape-only check; the instant check has its own case below.
        """
        self.assert_timestamp_shape("2025-12-16T22:11:11.001Z", "contract")

    def test_helper_accepts_a_freshly_built_contract_value(self):
        """The full check, shape and instant together, on a value built just now."""
        now = datetime.now(UTC)
        value = f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.{now.microsecond // 1000:03d}Z"
        self.assert_arena_timestamp(value, "fresh")


class ProgramRunInfoTimestampTest(TimestampAssertion, unittest.TestCase):
    """ProgramRunInfo sets all four fields in the contract format.

    These read the live clock, so they prove the real code path runs and emits the
    contract shape. They do not pin the zone: both sides of the instant check read
    the same machine clock, so on a UTC runner -- which is what the tests workflow
    gets, setting no TZ -- a naive-clock producer would pass every case here.
    ProgramRunInfoFixedClockTest is what pins the zone.
    """

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


class ProgramRunInfoFixedClockTest(TimestampAssertion, unittest.TestCase):
    """The producer really reads UTC, checked without consulting the runner's zone.

    Every case here drives ProgramRunInfo with program_info.datetime replaced by
    FixedNonUTCClock, then asserts the exact string. Because the fake's UTC and
    local readings differ by four hours by construction, swapping the producer's
    datetime.now(UTC) for datetime.now() changes the emitted value -- and so fails
    these -- under TZ=UTC just as it does anywhere else.
    """

    def assert_fixed_utc(self, value, field):
        """The emitted value must be the fake's UTC reading, not its local one."""
        self.assert_timestamp_shape(value, field)
        self.assertEqual(
            value,
            FIXED_UTC_RENDERING,
            f"{field} should be the clock's UTC reading {FIXED_UTC_RENDERING!r}; "
            f"got {value!r}"
            + (
                " -- that is the local reading, so the producer called "
                "datetime.now() rather than datetime.now(UTC)"
                if value == FIXED_LOCAL_RENDERING
                else ""
            ),
        )

    def test_the_fake_clock_readings_actually_differ(self):
        """Guard: if the fake's two readings ever agreed, this class would be vacuous."""
        utc_reading = FixedNonUTCClock.now(UTC)
        local_reading = FixedNonUTCClock.now()
        self.assertNotEqual(
            utc_reading.replace(tzinfo=None),
            local_reading,
            "the fake clock must read differently with and without a tz, or these "
            "cases cannot tell a UTC producer from a naive one",
        )
        self.assertNotEqual(FIXED_UTC_RENDERING, FIXED_LOCAL_RENDERING)

    def test_create_and_last_active_time_are_utc_instants(self):
        with mock.patch.object(program_info, "datetime", FixedNonUTCClock):
            info = ProgramRunInfo()
        for field in ("create_time", "last_active_time"):
            self.assert_fixed_utc(getattr(info, field), field)

    def test_msg_rcv_times_are_utc_instants(self):
        with mock.patch.object(program_info, "datetime", FixedNonUTCClock):
            info = ProgramRunInfo()
            info.msg_rcv()
        for field in ("last_rcv_time", "last_active_time"):
            self.assert_fixed_utc(getattr(info, field), field)

    def test_msg_publish_times_are_utc_instants(self):
        with mock.patch.object(program_info, "datetime", FixedNonUTCClock):
            info = ProgramRunInfo()
            info.msg_publish()
        for field in ("last_pub_time", "last_active_time"):
            self.assert_fixed_utc(getattr(info, field), field)

    def test_all_four_fields_are_utc_instants(self):
        with mock.patch.object(program_info, "datetime", FixedNonUTCClock):
            info = ProgramRunInfo()
            info.msg_rcv()
            info.msg_publish()
        for field in TIME_FIELDS:
            self.assert_fixed_utc(getattr(info, field), field)


class SceneProgramInfoTimestampTest(TimestampAssertion, unittest.IsolatedAsyncioTestCase):
    """The same four fields, driven through a real Scene and onto the wire.

    Plus one case on the envelope "timestamp" that rides along in the same payload,
    which the run-info fix does not touch and which is still malformed.
    """

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

    async def published_program_payloads(self, harness):
        """The program payloads the harness put on the wire, decoded.

        Drives a receive and a publish, then publishes the program object the way
        the periodic stats update does, and returns the whole payloads -- envelope
        included, not just data.program.
        """
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
        program_payloads = [
            p
            for p in payloads
            if isinstance(p.get("data"), dict)
            and ProgramRunInfo.object_type in p["data"]
        ]
        self.assertTrue(
            program_payloads, "no published program payload carried run_info"
        )
        return program_payloads

    async def test_run_info_fields_parse_in_the_published_program_payload(self):
        """The four data.program.* run-info fields, as published.

        Scoped to those four fields: the envelope "timestamp" that travels in the
        same payload is a separate value from a separate code path, pinned by
        test_published_envelope_timestamp_is_a_utc_instant below.
        """
        harness = await self.make_connected_harness()
        for payload in await self.published_program_payloads(harness):
            run_info = payload["data"][ProgramRunInfo.object_type]
            for field in TIME_FIELDS:
                self.assertIn(field, run_info, f"{field} missing from published run_info")
                self.assert_arena_timestamp(run_info[field], f"published {field}")

    async def test_published_envelope_timestamp_is_a_utc_instant(self):
        """The envelope "timestamp" is well-formed, on the same contract as the rest.

        The published payload carries a top-level "timestamp" built by the publish
        path in Scene._publish, separately from the four data.program.* values. It
        used to be built by the pre-fix expression, so a consumer of the
        scene-program topic saw four good values sitting next to one unparseable
        "...+00Z"; PR #247 replaced that expression with millisecond-precision
        Zulu formatting, so the envelope now holds to the same contract.

        Checked with the module's own assert_arena_timestamp, which is what the
        data.program.* cases use: shape *and* instant, so a publish path that went
        back to a numeric offset, to microsecond precision, or to a naive local
        clock under a "Z" all fail here.
        """
        harness = await self.make_connected_harness()
        for payload in await self.published_program_payloads(harness):
            self.assertIn(
                "timestamp", payload, "published program payload lost its envelope timestamp"
            )
            self.assert_arena_timestamp(payload["timestamp"], "envelope timestamp")


if __name__ == "__main__":
    unittest.main()
