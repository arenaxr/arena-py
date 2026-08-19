"""Tests that a private object always publishes to the private objects topic.

A private object (one carrying a truthy _private_userid) belongs on the
eight-level private topic, whose last token is the recipient's user id:

    ${realm}/s/${nameSpace}/${sceneName}/o/${userClient}/${objectId}/${toUid}

Scene._publish used to select that topic in an `elif` hanging off the
can_publish_obj permission pre-check. The failed-permission branch only reports
an error and falls through to the publish, so a False pre-check skipped the
private-topic rewrite entirely and the object went out on the seven-level public
objects topic instead, where every client in the scene can read it.

can_publish_obj is computed once at connect time against a seven-level objects
topic, so a token granting only private depth (realm/s/<ns>/<scene>/o/+/+/+)
leaves it False while still permitting the private publish. Topic selection must
therefore not depend on the boolean at all, which is what these tests pin: they
assert the captured topic for both values of it.

Two further properties are pinned here because nothing else in the suite pins
them:

- The marker is read for *truthiness*, not mere presence. Object.__init__ only
  stores _private_userid when it is truthy, but update_attributes() stores it
  whenever the key is passed, so update_object(obj, private_userid=None) - the
  documented way to make an object public again - leaves the attribute present
  and None. A presence check would then render a literal "None" recipient token.
- The permission error report sits *above* the private rewrite, so it names the
  seven-level topic can_publish_obj was actually computed against.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself.
"""

import contextlib
import io
import re
import unittest
from collections import namedtuple

from arena.objects import Object
from arena.test_system import ArenaE2ETest

PRIVATE_USER = "targetuser42"
PRIVATE_OBJECT_ID = "secret_box"
PUBLIC_OBJECT_ID = "public_box"

# The topic named inside the can_publish_obj failure message, which is built
# before the private rewrite runs.
REPORTED_TOPIC = re.compile(r"permission to publish to topic (\S+) on ")

Published = namedtuple("Published", ("topic", "scene", "stderr"))


class PrivateTopicSelectionTestCase(unittest.IsolatedAsyncioTestCase):
    """Publishes one object on a mock transport and inspects the captured topic.

    IsolatedAsyncioTestCase, and every test `async def`, even though none of them
    awaits anything: constructing ArenaE2ETest reaches EventLoop.__init__, which
    calls asyncio.get_event_loop(). Under a plain TestCase that raises
    RuntimeError("There is no current event loop") as soon as any earlier
    IsolatedAsyncioTestCase in the run has closed the thread's loop, so the whole
    file errors out under `unittest discover` while passing when run alone. The
    "coroutine was never awaited" warnings the harness emits come from
    ProgramRunInfo queueing worker coroutines that nothing runs, not from these
    test methods, and are present either way.
    """

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make_scene(can_publish_obj=True, private_userid=None):
        """A mock-transport scene with can_publish_obj forced, as (harness, scene)."""
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        scene = harness.scene
        if private_userid is not None:
            # Registers the recipient so Object.add_private() accepts it.
            scene.reset_private_objects(private_userid)
        scene.can_publish_obj = can_publish_obj
        return harness, scene

    @staticmethod
    def capture(harness, scene, publish):
        """Runs publish(), returning the single captured topic plus its stderr.

        stderr is captured rather than left to leak into the test output: the
        permission pre-check reports through it, and one test asserts on which
        topic that report names.
        """
        harness.transport.published_messages.clear()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            publish()
        published = harness.capture_published_messages()
        assert len(published) == 1, f"expected exactly one publish, got {published}"
        return Published(published[0]["topic"], scene, stderr.getvalue())

    @classmethod
    def publish_capturing_topic(cls, obj, can_publish_obj, private_userid=None):
        """Publishes obj() on a fresh scene with can_publish_obj forced."""
        harness, scene = cls.make_scene(can_publish_obj, private_userid)
        return cls.capture(harness, scene, lambda: scene._publish(obj(), "create"))

    @classmethod
    def publish_private_object(cls, can_publish_obj):
        """Publishes a private object."""
        return cls.publish_capturing_topic(
            lambda: Object(
                object_id=PRIVATE_OBJECT_ID, object_type="box", private_userid=PRIVATE_USER
            ),
            can_publish_obj,
            private_userid=PRIVATE_USER,
        )

    def public_topic_tokens(self, scene, object_id):
        """The seven-level public objects topic for object_id, as tokens."""
        params = scene.topicParams
        return [
            params["realm"],
            "s",
            params["nameSpace"],
            params["sceneName"],
            "o",
            params["userClient"],
            object_id,
        ]

    def assert_is_private_topic(self, topic, scene):
        """Asserts topic is the eight-level private topic for PRIVATE_OBJECT_ID."""
        self.assertEqual(
            topic.split("/"),
            [*self.public_topic_tokens(scene, PRIVATE_OBJECT_ID), PRIVATE_USER],
            f"not the private topic for {PRIVATE_USER}: {topic}",
        )

    async def test_private_object_uses_private_topic_without_publish_rights(self):
        """The leak: a False pre-check must not route a private object to the public topic."""
        published = self.publish_private_object(can_publish_obj=False)
        self.assertEqual(
            published.topic.split("/")[-1],
            PRIVATE_USER,
            f"private object leaked onto a non-private topic: {published.topic}",
        )
        self.assert_is_private_topic(published.topic, published.scene)

    async def test_private_object_uses_private_topic_with_publish_rights(self):
        """Happy-path control: this held before the fix too, and must keep holding."""
        published = self.publish_private_object(can_publish_obj=True)
        self.assert_is_private_topic(published.topic, published.scene)

    async def test_private_topic_ignores_publish_rights_entirely(self):
        """Both values of the boolean must select the same topic for the same object."""
        denied = self.publish_private_object(can_publish_obj=False)
        allowed = self.publish_private_object(can_publish_obj=True)
        self.assert_is_private_topic(denied.topic, denied.scene)
        self.assert_is_private_topic(allowed.topic, allowed.scene)
        # userClient carries a per-Scene random suffix, so drop it before comparing.
        denied_tokens = denied.topic.split("/")
        allowed_tokens = allowed.topic.split("/")
        del denied_tokens[5], allowed_tokens[5]
        self.assertEqual(denied_tokens, allowed_tokens)

    async def test_public_object_still_uses_public_topic_without_publish_rights(self):
        """Guard the other direction: a public object must not gain a recipient token."""
        published = self.publish_capturing_topic(
            lambda: Object(object_id=PUBLIC_OBJECT_ID, object_type="box"),
            can_publish_obj=False,
        )
        self.assertEqual(
            published.topic.split("/"),
            self.public_topic_tokens(published.scene, PUBLIC_OBJECT_ID),
            f"not the public objects topic: {published.topic}",
        )

    async def test_clearing_private_userid_returns_the_object_to_the_public_topic(self):
        """private_userid=None makes an object public again, so its topic must be public.

        Object.__init__ guards the marker with `if private_userid:`, but
        update_attributes() does not: it stores whatever was passed whenever the
        key is present. So after update_object(obj, private_userid=None) the
        attribute is present and None, and a presence check (hasattr) would
        select the private topic anyway and substitute() would render a literal
        "None" as the recipient token - addressing the object to a user named
        "None" instead of publishing it publicly. Reading the marker for
        truthiness, the way Object.add_private() does, is what keeps this test
        green.
        """
        harness, scene = self.make_scene(private_userid=PRIVATE_USER)
        obj = Object(object_id=PRIVATE_OBJECT_ID, object_type="box", private_userid=PRIVATE_USER)

        # Sanity: it really is on the private topic to begin with.
        private = self.capture(harness, scene, lambda: scene._publish(obj, "create"))
        self.assert_is_private_topic(private.topic, scene)

        public = self.capture(
            harness, scene, lambda: scene.update_object(obj, private_userid=None)
        )
        self.assertEqual(
            public.topic.split("/"),
            self.public_topic_tokens(scene, PRIVATE_OBJECT_ID),
            f"object made public again did not get the public topic: {public.topic}",
        )
        self.assertNotIn(
            "None",
            public.topic.split("/"),
            f"literal None rendered as a recipient token: {public.topic}",
        )

    async def test_permission_error_reports_the_precheck_topic(self):
        """The failed pre-check must name the seven-level topic it was computed against.

        can_publish_obj is a single boolean decided at connect time by testing
        one seven-level objects topic. When it is False, the complaint is about
        *that* topic, so the report is emitted above the private rewrite and
        names it - deliberately, even though the message then names a topic that
        is not the one this publish actually goes out on. Naming the eight-level
        private topic instead would attribute the pre-check's verdict to a topic
        the pre-check never tested, and under a private-depth-only grant that
        verdict does not apply to the private topic at all.

        This test therefore pins the *placement* of the report relative to the
        rewrite, which no assertion on the published topic can pin: moving the
        rewrite above the permission check leaves all the topic assertions green
        while silently changing what the message says.
        """
        published = self.publish_private_object(can_publish_obj=False)
        # The publish itself still goes to the private topic.
        self.assert_is_private_topic(published.topic, published.scene)

        reported = REPORTED_TOPIC.search(published.stderr)
        self.assertIsNotNone(
            reported, f"no permission error reported on stderr: {published.stderr!r}"
        )
        self.assertEqual(
            reported.group(1).split("/"),
            self.public_topic_tokens(published.scene, PRIVATE_OBJECT_ID),
            "the permission error must name the seven-level topic can_publish_obj "
            f"was computed against, not the topic published to: {reported.group(1)}",
        )


if __name__ == "__main__":
    unittest.main()
