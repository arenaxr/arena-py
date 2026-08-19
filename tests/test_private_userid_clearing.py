"""Tests that clearing private_userid fully returns an object to public.

update_object(obj, private_userid=None) is the documented way to make a private
object public again. Scene._publish now picks the topic from the marker's
*value*, so the object does go out on the public objects topic - but the object
model has to agree with that topic, and update_attributes() used to key off the
key's mere presence:

    if "private_userid" in kwargs:
        self._private_userid = kwargs.pop("private_userid")
        self.private = True

so clearing the marker still asserted `private` and never touched the per-user
Object.private_objects index. Three things followed, and each has a test here:

- the payload published on the public topic still carried "private": true;
- the object's private_objects entry outlived it. Object.remove() drops that
  entry by asking the object for its recipient, and a cleared object no longer
  names one, so delete_object() left the index holding a strong reference to a
  deleted object - the leak that Object.remove()'s de-indexing exists to prevent;
- delete_user_objects() for the *former* recipient walked that stale entry and
  dropped a now-public, still-live object out of Object.all_objects.

Re-targeting a private object from one recipient to another is pinned too, since
it de-indexes through the same path.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself.
"""

import contextlib
import io
import json
import unittest

from arena.objects import Object
from arena.test_system import ArenaE2ETest

OWNER = "alice"
OTHER = "bob"
OBJECT_ID = "secret_box"


class PrivateUseridClearingTestCase(unittest.IsolatedAsyncioTestCase):
    """Publishes and deletes one object on a mock transport.

    IsolatedAsyncioTestCase, and every test `async def`, for the reason spelled
    out in test_private_topic_selection.py: constructing ArenaE2ETest reaches
    asyncio.get_event_loop(), which raises under a plain TestCase once an earlier
    IsolatedAsyncioTestCase in the run has closed the thread's loop.
    """

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make_scene(*recipients):
        """A mock-transport scene with each recipient registered, as (harness, scene)."""
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        scene = harness.scene
        for recipient in recipients:
            # Registers the recipient so Object.add_private() accepts it.
            scene.reset_private_objects(recipient)
        return harness, scene

    @staticmethod
    def capture_payload(harness, publish):
        """Runs publish(), returning the single captured message's decoded payload.

        stderr is swallowed because the publish path reports permission
        complaints through it; nothing here asserts on them.
        """
        harness.transport.published_messages.clear()
        with contextlib.redirect_stderr(io.StringIO()):
            publish()
        published = harness.capture_published_messages()
        assert len(published) == 1, f"expected exactly one publish, got {published}"
        payload = published[0]["payload"]
        return json.loads(payload) if isinstance(payload, str) else payload

    def make_private_object(self, scene, recipient=OWNER):
        """A private object for recipient, indexed under it."""
        obj = Object(object_id=OBJECT_ID, object_type="box", private_userid=recipient)
        self.assertEqual(
            list(Object.private_objects[recipient]),
            [OBJECT_ID],
            "the object was not indexed under its recipient to begin with",
        )
        return obj

    def index_snapshot(self):
        """Object.private_objects with the inner dicts flattened to id lists."""
        return {user: sorted(objs) for user, objs in Object.private_objects.items()}

    async def test_cleared_object_publishes_without_the_private_flag(self):
        """The payload on the public topic must not still claim "private": true.

        `private` is the private-interaction flag, and a private object always
        carries it. Clearing the recipient has to clear it too, or the object
        lands on the public objects topic still asking the renderer to treat its
        interactions as private.

        The flag is dropped rather than set to False, so that a cleared object
        looks exactly like one created public: Scene.add_object() and
        update_object() read it as getattr(obj, "private", True), so storing
        False would also stop stamping program_id onto the object - a second,
        unrelated change to the payload. This test pins both halves.
        """
        harness, scene = self.make_scene(OWNER)
        obj = self.make_private_object(scene)

        private_payload = self.capture_payload(
            harness, lambda: scene.update_object(obj, position=(1, 1, 1))
        )
        self.assertIs(
            private_payload.get("private"),
            True,
            f"a private object should carry private: true: {private_payload}",
        )

        public_payload = self.capture_payload(
            harness, lambda: scene.update_object(obj, private_userid=None)
        )
        self.assertNotIn(
            "private",
            public_payload,
            f"object returned to public still carries a private flag: {public_payload}",
        )
        self.assertEqual(
            public_payload.get("program_id"),
            private_payload.get("program_id"),
            "clearing the recipient should not disturb program_id",
        )

    async def test_clearing_the_recipient_empties_the_private_index(self):
        """The private_objects entry must go when the recipient does.

        Object.remove() cannot clean this up later: it finds the entry by asking
        the object which recipient it belongs to, and a cleared object answers
        None. So the entry has to be dropped here, while the former recipient is
        still known - otherwise it survives delete_object() as a strong
        reference to an object that is gone from the scene.
        """
        harness, scene = self.make_scene(OWNER)
        obj = self.make_private_object(scene)

        with contextlib.redirect_stderr(io.StringIO()):
            scene.update_object(obj, private_userid=None)
        self.assertEqual(
            self.index_snapshot(),
            {OWNER: []},
            "clearing the recipient left the object in the private index",
        )

        # And nothing is left holding the object after it is deleted.
        with contextlib.redirect_stderr(io.StringIO()):
            scene.delete_object(obj)
        self.assertEqual(self.index_snapshot(), {OWNER: []})
        self.assertNotIn(OBJECT_ID, Object.all_objects)

    async def test_delete_user_objects_leaves_a_cleared_object_alone(self):
        """A now-public object must survive its former recipient's cleanup.

        delete_user_objects(userid) walks that user's private_objects entry and
        drops each id from all_objects. An object returned to public is no
        longer that user's, so a stale entry would take a live, public object out
        of the scene's object store when the user left.
        """
        harness, scene = self.make_scene(OWNER)
        obj = self.make_private_object(scene)

        with contextlib.redirect_stderr(io.StringIO()):
            scene.update_object(obj, private_userid=None)
        scene.delete_user_objects(OWNER)

        self.assertIs(
            Object.all_objects.get(OBJECT_ID),
            obj,
            "the former recipient's cleanup dropped an object that is now public",
        )
        self.assertNotIn(OWNER, Object.private_objects)

    async def test_retargeting_moves_the_object_between_recipients(self):
        """A new recipient means exactly one index entry, under the new user.

        Same mechanism as clearing: the object stops being able to name its old
        recipient the moment the marker is overwritten, so the old entry has to
        be dropped in the same breath as the new one is added. Leaving the old
        entry in place would let delete_user_objects() for the old recipient
        drop an object that is now private to the new one.
        """
        harness, scene = self.make_scene(OWNER, OTHER)
        obj = self.make_private_object(scene)

        with contextlib.redirect_stderr(io.StringIO()):
            scene.update_object(obj, private_userid=OTHER)

        self.assertEqual(
            self.index_snapshot(),
            {OWNER: [], OTHER: [OBJECT_ID]},
            "re-targeting did not move the object between recipients",
        )
        self.assertIs(Object.private_objects[OTHER][OBJECT_ID], obj)

        scene.delete_user_objects(OWNER)
        self.assertIs(
            Object.all_objects.get(OBJECT_ID),
            obj,
            "the old recipient's cleanup dropped an object private to the new one",
        )

    async def test_explicit_private_flag_wins_over_clearing_the_recipient(self):
        """private=True in the same call survives, matching Object.__init__.

        A public object may still want private interactions - private clicks,
        mouseover and so on - which is what the `private` flag alone means.
        __init__ takes `private` from its kwargs and only forces it True when a
        recipient is given, so an explicit private= has to outrank the implicit
        clearing done here.

        Unlike the tests above this one pins a precedence rule rather than a
        fixed defect: it passes against the old code too, which asserted
        `private` unconditionally.
        """
        harness, scene = self.make_scene(OWNER)
        obj = self.make_private_object(scene)

        payload = self.capture_payload(
            harness,
            lambda: scene.update_object(obj, private=True, private_userid=None),
        )
        self.assertIs(
            payload.get("private"),
            True,
            f"an explicit private=True was dropped along with the recipient: {payload}",
        )
        self.assertEqual(
            payload["object_id"], OBJECT_ID, "unexpected object published"
        )
        # Still returned to public: the recipient is gone from the index.
        self.assertEqual(self.index_snapshot(), {OWNER: []})


if __name__ == "__main__":
    unittest.main()
