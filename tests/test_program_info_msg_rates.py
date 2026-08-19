"""Tests for the published-message rate ProgramRunInfo reports.

ProgramRunInfo keeps two counters, rcv_msgs and pub_msgs, and turns each into a
moving average -- avg_rcv_msgs_per_sec and avg_pub_msgs_per_sec -- that rides to
consumers in the published program object, alongside the run-info timestamps.

Each average is a delta over an interval, so it needs the count as of the previous
interval to subtract. _update_stats keeps those baselines in _rcv_msgs_start and
_pub_msgs_start. The published baseline must track the *published* counter: rebase
it on the received counter instead and the published delta becomes
pub_msgs - rcv_msgs, which is wrong as soon as the two counters diverge and goes
negative as soon as more messages arrive than are sent -- the ordinary case for a
program that mostly listens. A rate of messages published cannot be negative, so
that is a value no consumer can make sense of.

These cases pin the averages across a receive-and-publish sequence with the
counters deliberately diverged, driving _update_stats through a fake clock so the
expected numbers are exact rather than timing-dependent.
"""

import unittest
from datetime import UTC, datetime, timedelta
from unittest import mock

from arena.utils import ProgramRunInfo
from arena.utils import program_info


class SteppableClock:
    """Stands in for the `datetime` the program_info module calls `now` on.

    _update_stats derives its interval from datetime.now(), and returns early
    unless a whole second has passed, so a test that wants exact per-second rates
    cannot use the real clock. This one only moves when advance() says so.
    """

    def __init__(self, start=datetime(2026, 8, 19, 12, 0, 0, tzinfo=UTC)):
        self._start = start
        self._elapsed = timedelta()

    def advance(self, seconds):
        self._elapsed += timedelta(seconds=seconds)

    def now(self, tz=None):
        instant = self._start + self._elapsed
        if tz is None:
            # datetime.now(): a naive local wall-clock reading.
            return instant.replace(tzinfo=None)
        return instant.astimezone(tz)


class ProgramRunInfoMsgRateTest(unittest.TestCase):
    """The two moving averages, over a sequence where the counters diverge."""

    def drive(self, clock, info, rcv, pub, advance_to):
        """Record `rcv` receives and `pub` publishes, then run one stats update.

        advance_to is measured from construction, not from the previous update,
        because _update_stats does not reset its interval start -- so the interval
        it sees grows across updates. That is existing behaviour and not what these
        cases are about; they just have to predict it to assert exact numbers.
        """
        with mock.patch.object(program_info, "datetime", clock):
            for _ in range(rcv):
                info.msg_rcv()
            for _ in range(pub):
                info.msg_publish()
            clock._elapsed = timedelta(seconds=advance_to)
            info._update_stats()

    def make_info(self, clock):
        with mock.patch.object(program_info, "datetime", clock):
            return ProgramRunInfo()

    def test_published_baseline_starts_from_the_published_counter(self):
        """Both counters are 0 at construction, so read the attribute, not the value."""
        clock = SteppableClock()
        info = self.make_info(clock)
        self.assertEqual(info._rcv_msgs_start, info.rcv_msgs)
        self.assertEqual(
            info._pub_msgs_start,
            info.pub_msgs,
            "the published baseline must be seeded from pub_msgs",
        )

    def test_avg_pub_msgs_per_sec_across_a_receive_and_publish_sequence(self):
        """The pinned numbers: 20 rcv / 2 pub over 2s, then 4 rcv / 2 pub more by 4s.

        Interval 1 -- 20 received and 2 published in 2s -- gives 10.0 and 1.0 per
        second, and with one sample so far the average is that sample.

        Interval 2 -- 4 more received and 2 more published, at 4s from the start --
        gives 4/4 = 1.0 received and 2/4 = 0.5 published per second. With N=2 the
        averages move halfway: 10.0 -> 5.5 and 1.0 -> 0.75.

        Rebasing the published baseline on rcv_msgs makes interval 2's published
        delta 4 - 20 = -16, i.e. -4.0 per second, dragging the published average to
        -1.5: negative, and reported as a rate of messages sent.
        """
        clock = SteppableClock()
        info = self.make_info(clock)

        self.drive(clock, info, rcv=20, pub=2, advance_to=2)
        self.assertEqual(info.rcv_msgs, 20)
        self.assertEqual(info.pub_msgs, 2)
        self.assertEqual(info.avg_rcv_msgs_per_sec, 10.0)
        self.assertEqual(info.avg_pub_msgs_per_sec, 1.0)

        self.drive(clock, info, rcv=4, pub=2, advance_to=4)
        self.assertEqual(info.rcv_msgs, 24)
        self.assertEqual(info.pub_msgs, 4)
        self.assertEqual(info.avg_rcv_msgs_per_sec, 5.5)
        self.assertEqual(
            info.avg_pub_msgs_per_sec,
            0.75,
            "the published average should reflect 2 publishes over the 4s interval; "
            "-1.5 means the published delta was rebased on the received counter",
        )

    def test_published_average_never_goes_negative_while_receives_outpace_publishes(self):
        """The symptom a consumer would see, asserted directly over more intervals.

        Every interval here publishes at least one message, so the true rate is
        positive throughout and no moving average of it can be negative.
        """
        clock = SteppableClock()
        info = self.make_info(clock)

        elapsed = 0
        for rcv, pub in ((30, 1), (30, 1), (30, 2), (30, 1), (30, 2)):
            elapsed += 2
            self.drive(clock, info, rcv=rcv, pub=pub, advance_to=elapsed)
            self.assertGreater(
                info.avg_pub_msgs_per_sec,
                0,
                f"published average went to {info.avg_pub_msgs_per_sec} after an "
                f"interval that published {pub} message(s); a rate of messages "
                f"published cannot be negative",
            )

        self.assertEqual(info.rcv_msgs, 150)
        self.assertEqual(info.pub_msgs, 7)

    def test_published_baseline_tracks_the_published_counter_across_updates(self):
        """White-box: after an update the baseline equals pub_msgs, not rcv_msgs."""
        clock = SteppableClock()
        info = self.make_info(clock)
        self.drive(clock, info, rcv=9, pub=3, advance_to=2)
        self.assertEqual(info._rcv_msgs_start, 9)
        self.assertEqual(
            info._pub_msgs_start,
            3,
            "after an update the published baseline must be pub_msgs (3), not "
            "rcv_msgs (9)",
        )


if __name__ == "__main__":
    unittest.main()
