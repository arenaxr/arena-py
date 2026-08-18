"""Tests for client-side orphan reaping (Object.remove_descendants).

The ARENA server publishes a single delete for the object that was deleted, so
clients must drop that object's descendants from their own state themselves.

Object.all_objects and Object.private_objects are global class state, so every
test clears them before and after itself to avoid leaking objects into the rest
of the suite. Scene._last_published_state (the delta-compression shadow map) is
per-scene, so it goes away with the harness that owns it.
"""

import contextlib
import io
import unittest
from unittest.mock import patch

from arena.objects import Object
from arena.test_system import ArenaE2ETest


class FakeTask:
    """Stand-in for an asyncio task queued in Object.delayed_prop_tasks."""

    def __init__(self):
        self.cancelled = False

    def cancel(self):
        self.cancelled = True


class ReapTestCase(unittest.TestCase):
    """Base case that keeps the global object store clean."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make(object_id, parent=None):
        if parent is None:
            return Object(object_id=object_id)
        return Object(object_id=object_id, parent=parent)

    @staticmethod
    def reap_capturing_output(object_id):
        """Reaps object_id, returning (reaped_ids, anything printed).

        The library reports warnings with print("[WARNING]", ...), so the bound
        warnings are asserted on stdout rather than through the logging module.
        """
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            reaped = Object.remove_descendants(object_id)
        return reaped, captured.getvalue()


class TestRemoveDescendants(ReapTestCase):
    def test_multi_level_tree_fully_reaped(self):
        """Every generation below the deleted object is dropped, not just children."""
        self.make("root")
        self.make("child", parent="root")
        self.make("grandchild", parent="child")
        self.make("great_grandchild", parent="grandchild")

        Object.remove(Object.get("root"))
        reaped = Object.remove_descendants("root")

        self.assertEqual(sorted(reaped), ["child", "grandchild", "great_grandchild"])
        self.assertEqual(Object.all_objects, {})

    def test_siblings_and_unrelated_objects_survive(self):
        """Only the deleted object's own subtree is reaped."""
        self.make("root")
        self.make("kept_sibling")            # shares no parent with root's subtree
        self.make("doomed", parent="root")
        self.make("doomed_child", parent="doomed")
        self.make("kept_child", parent="kept_sibling")
        self.make("unrelated")

        Object.remove(Object.get("root"))
        reaped = Object.remove_descendants("root")

        self.assertEqual(sorted(reaped), ["doomed", "doomed_child"])
        self.assertEqual(sorted(Object.all_objects), ["kept_child", "kept_sibling", "unrelated"])

    def test_object_with_no_children_removes_cleanly(self):
        """A leaf delete reaps nothing and leaves the rest of the scene alone."""
        self.make("leaf")
        self.make("bystander")

        Object.remove(Object.get("leaf"))
        reaped = Object.remove_descendants("leaf")

        self.assertEqual(reaped, [])
        self.assertEqual(sorted(Object.all_objects), ["bystander"])

    def test_cycle_in_parent_pointers_terminates(self):
        """A cycle of parent pointers is reaped once instead of looping forever."""
        # a -> b -> c -> a: a malformed chain a naive walk would follow forever.
        self.make("a", parent="c")
        self.make("b", parent="a")
        self.make("c", parent="b")
        self.make("unrelated")

        Object.remove(Object.get("a"))
        reaped = Object.remove_descendants("a")

        self.assertEqual(sorted(reaped), ["b", "c"])
        self.assertEqual(sorted(Object.all_objects), ["unrelated"])

    def test_self_parented_object_terminates(self):
        """An object that is its own parent does not reap (or revisit) itself."""
        self.make("loop", parent="loop")

        Object.remove(Object.get("loop"))
        self.assertEqual(Object.remove_descendants("loop"), [])
        self.assertEqual(Object.all_objects, {})

    def test_descendant_bound_stops_walk_and_warns(self):
        """MAX_REAP_DESCENDANTS caps how many objects one delete may reap."""
        self.make("root")
        for i in range(6):
            self.make(f"child{i}", parent="root")

        Object.remove(Object.get("root"))
        with patch.object(Object, "MAX_REAP_DESCENDANTS", 3):
            reaped, output = self.reap_capturing_output("root")

        self.assertEqual(len(reaped), 3)
        # The walk stopped: the remaining children are still in the store.
        self.assertEqual(len(Object.all_objects), 3)
        self.assertIn("[WARNING]", output)
        self.assertIn("root", output)                    # names the deleted object
        self.assertIn("3 objects", output)               # names how many were reaped
        self.assertIn("MAX_REAP_DESCENDANTS (3)", output)  # names the bound that was hit

    def test_depth_bound_stops_walk_and_warns(self):
        """MAX_REAP_DEPTH caps how deep below the deleted object reaping follows."""
        self.make("root")
        parent = "root"
        for i in range(5):
            self.make(f"level{i}", parent=parent)
            parent = f"level{i}"

        Object.remove(Object.get("root"))
        with patch.object(Object, "MAX_REAP_DEPTH", 2):
            reaped, output = self.reap_capturing_output("root")

        self.assertEqual(sorted(reaped), ["level0", "level1"])
        self.assertEqual(sorted(Object.all_objects), ["level2", "level3", "level4"])
        self.assertIn("[WARNING]", output)
        self.assertIn("root", output)              # names the deleted object
        self.assertIn("2 objects", output)         # names how many were reaped
        self.assertIn("MAX_REAP_DEPTH (2)", output)  # names the bound that was hit

    def test_no_warning_when_walk_completes_within_bounds(self):
        """Bounds that are not reached stay silent."""
        self.make("root")
        self.make("child", parent="root")

        Object.remove(Object.get("root"))
        with patch.object(Object, "MAX_REAP_DEPTH", 2), patch.object(Object, "MAX_REAP_DESCENDANTS", 2):
            reaped, output = self.reap_capturing_output("root")

        self.assertEqual(reaped, ["child"])
        self.assertEqual(output, "")

    def test_delayed_prop_tasks_cancelled_for_descendants(self):
        """Reaping goes through Object.remove, so pending tasks are cancelled."""
        self.make("root")
        child = self.make("child", parent="root")
        grandchild = self.make("grandchild", parent="child")
        survivor = self.make("survivor")

        child_task = FakeTask()
        grandchild_task = FakeTask()
        survivor_task = FakeTask()
        child.delayed_prop_tasks = {"position": child_task}
        grandchild.delayed_prop_tasks = {"rotation": grandchild_task}
        survivor.delayed_prop_tasks = {"scale": survivor_task}

        Object.remove(Object.get("root"))
        Object.remove_descendants("root")

        self.assertTrue(child_task.cancelled)
        self.assertTrue(grandchild_task.cancelled)
        self.assertFalse(survivor_task.cancelled)

    def test_reaping_is_safe_when_descendant_already_gone(self):
        """A descendant removed between the index scan and the walk is skipped."""
        self.make("root")
        child = self.make("child", parent="root")
        self.make("grandchild", parent="child")

        Object.remove(Object.get("root"))
        real_remove = Object.remove

        def remove_and_race(obj):
            # Simulate a concurrent delete of the grandchild while the child is
            # being reaped; the walk must not raise KeyError on it.
            real_remove(obj)
            if obj.object_id == "child":
                Object.all_objects.pop("grandchild", None)

        with patch.object(Object, "remove", staticmethod(remove_and_race)):
            reaped = Object.remove_descendants("root")

        self.assertEqual(reaped, ["child"])
        self.assertEqual(Object.all_objects, {})


class TestPrivateObjectCleanup(ReapTestCase):
    """Object.remove() owns the private_objects index, for reaps and single deletes."""

    USER = "private_user"

    def setUp(self):
        super().setUp()
        # add_private() requires the per-user bucket to exist; a scene creates it
        # (via reset_private_objects) when the user joins.
        Object.private_objects[self.USER] = {}

    def make_private(self, object_id, parent=None):
        kwargs = {"object_id": object_id, "private_userid": self.USER}
        if parent is not None:
            kwargs["parent"] = parent
        return Object(**kwargs)

    def test_reaped_private_descendants_dropped_from_private_objects(self):
        """A cascade drops private descendants from both indexes, not just all_objects."""
        self.make("root")
        self.make_private("private_child", parent="root")
        self.make_private("private_grandchild", parent="private_child")
        self.make_private("private_bystander")

        Object.remove(Object.get("root"))
        reaped = Object.remove_descendants("root")

        self.assertEqual(sorted(reaped), ["private_child", "private_grandchild"])
        self.assertEqual(sorted(Object.private_objects[self.USER]), ["private_bystander"])
        self.assertEqual(sorted(Object.all_objects), ["private_bystander"])

    def test_remove_drops_private_entry_for_single_object(self):
        """The single-object delete path is cleaned by the same code."""
        obj = self.make_private("lone_private")

        Object.remove(obj)

        self.assertEqual(Object.private_objects[self.USER], {})
        self.assertEqual(Object.all_objects, {})

    def test_remove_public_object_leaves_private_index_alone(self):
        """A public delete does not touch another user's private entries."""
        public = self.make("public_obj")
        self.make_private("private_obj")

        Object.remove(public)

        self.assertEqual(sorted(Object.private_objects[self.USER]), ["private_obj"])

    def test_remove_is_safe_when_private_bucket_is_gone(self):
        """A private object outliving its user's bucket removes without raising."""
        obj = self.make_private("orphan_private")
        # delete_user_objects() drops the whole per-user bucket on user leave.
        del Object.private_objects[self.USER]

        Object.remove(obj)  # must not raise

        self.assertEqual(Object.all_objects, {})


class SceneReapTestCase(unittest.IsolatedAsyncioTestCase):
    """Base case for reaping through a Scene, on a mock transport."""

    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    @staticmethod
    def make_harness(delta_compression=False):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()  # drop objects loaded from mock persist
        # The harness turns delta compression off for trace replay; the shadow map
        # is only populated when it is on.
        harness.scene.delta_compression = delta_compression
        return harness

    @staticmethod
    def make_tree(scene, publish=False):
        """Builds parent -> child -> grandchild plus a bystander, optionally published."""
        objs = [
            Object(object_id="reap_parent", object_type="box"),
            Object(object_id="reap_child", object_type="box", parent="reap_parent"),
            Object(object_id="reap_grandchild", object_type="box", parent="reap_child"),
            Object(object_id="reap_bystander", object_type="box"),
        ]
        if publish:
            for obj in objs:
                scene.add_object(obj)
        return objs[0]

    async def inject_delete(self, harness, object_id):
        """Injects a server delete for object_id, as the inbound handler sees it."""
        harness._start_tasks()
        for _ in range(10):  # subscriptions are set up by the connect task
            if harness.transport.subscriptions:
                break
            await harness.run_step(0.1)
        harness.inject_message(
            f"realm/s/user/test_scene/o/other_client/{object_id}",
            {"object_id": object_id, "action": "delete", "type": "object"},
        )
        await harness.run_step(0.1)


class TestSceneDeleteObjectReaps(SceneReapTestCase):
    """scene.delete_object must reap locally, not just publish one delete."""

    async def test_delete_object_reaps_descendants(self):
        harness = self.make_harness()
        parent = self.make_tree(harness.scene)

        harness.scene.delete_object(parent)
        await harness.run_step(0.1)

        self.assertEqual(sorted(harness.scene.all_objects), ["reap_bystander"])

    async def test_delete_object_clears_shadow_map_for_root_and_descendants(self):
        """delete_object publishes a custom payload, which skips _apply_delta's cleanup."""
        harness = self.make_harness(delta_compression=True)
        parent = self.make_tree(harness.scene, publish=True)
        shadow = harness.scene._last_published_state
        for object_id in ("reap_parent", "reap_child", "reap_grandchild", "reap_bystander"):
            self.assertIn(object_id, shadow)  # publishing recorded each one

        harness.scene.delete_object(parent)
        await harness.run_step(0.1)

        self.assertNotIn("reap_parent", shadow)      # the deleted object itself
        self.assertNotIn("reap_child", shadow)       # reaped descendants
        self.assertNotIn("reap_grandchild", shadow)
        self.assertIn("reap_bystander", shadow)      # untouched object keeps its state

    async def test_delete_object_of_unpublished_object_does_not_raise(self):
        """Nothing was published, so no shadow-map key exists to clear."""
        harness = self.make_harness(delta_compression=True)
        parent = self.make_tree(harness.scene)
        self.assertEqual(harness.scene._last_published_state, {})

        harness.scene.delete_object(parent)  # must not raise
        await harness.run_step(0.1)

        self.assertEqual(sorted(harness.scene.all_objects), ["reap_bystander"])

    async def test_delete_object_drops_reaped_private_descendants(self):
        """get_private_objects() must not return objects the cascade deleted."""
        harness = self.make_harness()
        harness.scene.reset_private_objects("private_user")
        parent = Object(object_id="reap_parent", object_type="box")
        Object(
            object_id="reap_private_child",
            object_type="box",
            parent="reap_parent",
            private_userid="private_user",
        )
        Object(
            object_id="reap_private_bystander",
            object_type="box",
            private_userid="private_user",
        )

        harness.scene.delete_object(parent)
        await harness.run_step(0.1)

        self.assertEqual(
            sorted(harness.scene.get_private_objects("private_user")),
            ["reap_private_bystander"],
        )


class TestSceneInboundDeleteReaps(SceneReapTestCase):
    """An inbound server delete must clean up the same local state."""

    async def test_inbound_delete_reaps_descendants(self):
        harness = self.make_harness()
        self.make_tree(harness.scene)

        await self.inject_delete(harness, "reap_parent")

        # Asserted per object_id: starting the scene tasks also loads the
        # harness's mock persist objects into the store.
        self.assertNotIn("reap_parent", harness.scene.all_objects)
        self.assertNotIn("reap_child", harness.scene.all_objects)
        self.assertNotIn("reap_grandchild", harness.scene.all_objects)
        self.assertIn("reap_bystander", harness.scene.all_objects)

    async def test_inbound_delete_clears_shadow_map_for_root_and_descendants(self):
        """Objects this scene published are forgotten when the server deletes them."""
        harness = self.make_harness(delta_compression=True)
        self.make_tree(harness.scene, publish=True)
        shadow = harness.scene._last_published_state
        for object_id in ("reap_parent", "reap_child", "reap_grandchild", "reap_bystander"):
            self.assertIn(object_id, shadow)  # publishing recorded each one

        await self.inject_delete(harness, "reap_parent")

        self.assertNotIn("reap_parent", shadow)      # the deleted object itself
        self.assertNotIn("reap_child", shadow)       # reaped descendants
        self.assertNotIn("reap_grandchild", shadow)
        self.assertIn("reap_bystander", shadow)      # untouched object keeps its state

    async def test_inbound_delete_of_unpublished_object_does_not_raise(self):
        """A delete for objects with no shadow-map entry still reaps cleanly."""
        harness = self.make_harness(delta_compression=True)
        self.make_tree(harness.scene)
        self.assertEqual(harness.scene._last_published_state, {})

        await self.inject_delete(harness, "reap_parent")

        self.assertNotIn("reap_parent", harness.scene.all_objects)
        self.assertNotIn("reap_child", harness.scene.all_objects)
        self.assertNotIn("reap_grandchild", harness.scene.all_objects)
        self.assertIn("reap_bystander", harness.scene.all_objects)


class TestForgetPublishedState(SceneReapTestCase):
    """The shadow-map helper is tolerant of ids it has never seen."""

    async def test_unknown_object_ids_are_ignored(self):
        """Ids with no entry are skipped, and the known id is still forgotten."""
        harness = self.make_harness(delta_compression=True)
        harness.scene._last_published_state["published"] = {"object_type": "box"}

        harness.scene._forget_published_state(
            ["never_published", "published", "also_missing"]
        )

        self.assertEqual(harness.scene._last_published_state, {})


if __name__ == "__main__":
    unittest.main()
