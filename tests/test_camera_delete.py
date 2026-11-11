"""Regression tests for routing inbound camera deletes."""

import unittest

from arena.objects import Object
from arena.test_system import ArenaE2ETest
from arena.topics import PUBLISH_TOPICS


class CameraDeleteTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    async def make_harness(self):
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        Object.all_objects.clear()
        await harness.start_and_wait_until_subscribed()
        return harness

    async def inject(self, harness, object_id, action, data=None):
        payload = {"object_id": object_id, "action": action, "type": "object"}
        if data is not None:
            payload["data"] = data
        topic = PUBLISH_TOPICS.SCENE_OBJECTS.substitute(
            realm="realm", nameSpace="user", sceneName="test_scene",
            userClient="other_client", objectId=object_id,
        )
        harness.inject_message(topic, payload)
        await harness.run_step(0.1)
        payload["topic"] = topic
        return payload

    async def test_registered_v1_and_v2_camera_deletes(self):
        harness = await self.make_harness()
        left, deleted = [], []
        harness.scene.user_left_callback = lambda scene, obj, msg: left.append((obj, msg))
        harness.scene.delete_obj_callback = lambda scene, obj, msg: deleted.append((obj, msg))

        for object_id in ("camera_jdoe_1448081341", "jdoe_1448081341"):
            with self.subTest(object_id=object_id):
                await self.inject(harness, object_id, "create", {"object_type": "camera"})
                camera = harness.scene.users[object_id]
                payload = await self.inject(harness, object_id, "delete")
                self.assertEqual(left[-1:], [(camera, payload)])
                self.assertNotIn(object_id, harness.scene.users)
                self.assertNotIn(object_id, harness.scene.all_objects)
        self.assertEqual(len(left), 2)
        self.assertEqual(deleted, [])

    async def test_v2_camera_delete_without_left_callback(self):
        harness = await self.make_harness()
        object_id = "jdoe_1448081341"
        await self.inject(harness, object_id, "create", {"object_type": "camera"})
        deleted = []
        harness.scene.delete_obj_callback = lambda scene, obj, msg: deleted.append(obj)

        await self.inject(harness, object_id, "delete")

        self.assertNotIn(object_id, harness.scene.users)
        self.assertNotIn(object_id, harness.scene.all_objects)
        self.assertEqual(deleted, [])

    async def test_ordinary_object_with_camera_in_id(self):
        harness = await self.make_harness()
        object_id = "camera_tripod"
        left, deleted = [], []
        harness.scene.user_left_callback = lambda scene, obj, msg: left.append(obj)
        harness.scene.delete_obj_callback = lambda scene, obj, msg: deleted.append((obj, msg))
        await self.inject(harness, object_id, "create", {"object_type": "box"})
        obj = harness.scene.all_objects[object_id]

        payload = await self.inject(harness, object_id, "delete")

        self.assertEqual(deleted, [(obj, payload)])
        self.assertEqual(left, [])
        self.assertNotIn(object_id, harness.scene.all_objects)
