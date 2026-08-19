"""Tests that Camera.__init__ always builds a complete object.

Camera fills in its arena-user fields itself and then calls Object.__init__ to
do the rest: object_id, data, type, persist, and registration in all_objects.
That call used to be made from one branch per pose combination -- position and
rotation, position only, rotation only -- with no branch for a data dict
carrying neither. A camera built from such a dict got no Object.__init__ call at
all, so it came back half-built and raised KeyError: 'data' from json() later,
somewhere unrelated to the message that caused it.

An arena-user-only update is exactly that shape, and it arrives from the scene
as Camera(**payload), so these pin the no-pose cases as well as the ones the
original branches covered.

Object.all_objects is global class state, so each test clears it either side of
itself rather than leaking cameras into the rest of the suite.
"""

import json
import unittest

from arena.objects import Camera, Object


class CameraInitTestCase(unittest.TestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    # the pose combinations Camera can be handed, including the two that used to
    # fall off the end of the branch chain
    POSES = {
        "position_and_rotation": {
            "position": {"x": 0, "y": 1.6, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
        },
        "position_only": {"position": {"x": 0, "y": 1.6, "z": 0}},
        "rotation_only": {"rotation": {"x": 0, "y": 0, "z": 0, "w": 1}},
        "neither": {},
    }

    def test_object_init_runs_for_every_pose_combination(self):
        """Every camera gets the fields Object.__init__ is responsible for.

        "type" is asserted on the published payload rather than as
        camera.type: Object carries type = "object" as a class attribute with
        the same value, so the attribute form reads back "object" whether or not
        Object.__init__ ever ran and cannot fail.
        """
        for name, pose in self.POSES.items():
            with self.subTest(pose=name):
                Object.all_objects.clear()
                camera = Camera(f"camera_{name}_1", data=dict(pose))

                self.assertEqual(camera.object_id, f"camera_{name}_1")
                self.assertIn("data", camera)
                self.assertEqual(json.loads(camera.json())["type"], "object")
                self.assertFalse(camera.persist)

    def test_camera_is_registered_in_all_objects(self):
        """A camera the library built has to be findable, or the scene rebuilds it.

        Object.get / Object.exists are how the scene decides whether it already
        knows a user; an unregistered camera means a second one for the same id.
        """
        for name, pose in self.POSES.items():
            with self.subTest(pose=name):
                Object.all_objects.clear()
                camera = Camera(f"camera_{name}_2", data=dict(pose))

                self.assertTrue(Object.exists(f"camera_{name}_2"))
                self.assertIs(Object.get(f"camera_{name}_2"), camera)

    def test_json_does_not_raise(self):
        """json() indexes the data key Object.__init__ creates."""
        for name, pose in self.POSES.items():
            with self.subTest(pose=name):
                Object.all_objects.clear()
                camera = Camera(f"camera_{name}_3", data=dict(pose))

                payload = json.loads(camera.json())

                self.assertEqual(payload["object_id"], f"camera_{name}_3")
                self.assertIn("data", payload)

    def test_arena_user_only_update_builds_a_usable_camera(self):
        """The shape that motivated this: arena-user fields and no pose at all.

        Both halves have to survive -- the arena-user fields Camera reads for
        itself, and the object fields Object.__init__ provides.

        The payload assertion is on the round-tripped contents, not just on a
        "data" key being present, and the arena-user fields are read back off
        the wire rather than off the instance. Camera reads displayName and
        hasAudio out of the raw dict before super() runs, so those attributes
        survive an Object.__init__ that never receives the caller's kwargs at
        all -- the caller's whole data dict, plus persist / ttl / private /
        private_userid, would be replaced by a default pose and nothing here
        would notice.
        """
        camera = Camera(
            "camera_1_1",
            data={"arena-user": {"displayName": "bob", "hasAudio": True}},
            persist=True,
        )

        self.assertEqual(camera.displayName, "bob")
        self.assertTrue(camera.hasAudio)
        self.assertEqual(camera.hands, {})
        self.assertEqual(camera.object_id, "camera_1_1")
        self.assertIn("camera_1_1", Object.all_objects)

        payload = json.loads(camera.json())
        self.assertEqual(
            payload["data"], {"arena-user": {"displayName": "bob", "hasAudio": True}}
        )
        self.assertEqual(payload["data"]["arena-user"]["displayName"], "bob")
        self.assertTrue(payload["persist"])

    def test_camera_with_no_data_at_all_is_complete(self):
        """Camera(object_id) with no data dict is the same no-pose case."""
        camera = Camera("camera_3_3")

        self.assertEqual(camera.object_id, "camera_3_3")
        self.assertIn("data", camera)
        self.assertIn("camera_3_3", Object.all_objects)

    def test_object_type_is_camera(self):
        """object_type is what the scene routes a payload on; it must be set.

        Asserted on the published payload, because object_type is never an
        instance attribute: Camera passes it to super() as a kwarg and
        Object.__init__ folds it into data. camera.object_type therefore
        resolves to Camera's class attribute and reads back "camera" for any
        implementation at all -- including one that never passes object_type to
        super(), whose payload publishes the Object default "entity" instead.

        The no-data-dict form is the one that can be asserted this way.
        Object.__init__ builds data from kwargs.get("data", kwargs), so a
        caller-supplied data dict is used as given and the object_type kwarg
        never reaches the payload beside it; that is Object's behaviour, not
        Camera's, and the pose combinations are covered by the tests above.
        """
        camera = Camera("camera_5_5")

        payload = json.loads(camera.json())

        self.assertEqual(payload["data"]["object_type"], "camera")

    def test_pose_is_preserved_where_it_was_given(self):
        """Adding the missing case must not disturb the ones that worked."""
        camera = Camera(
            "camera_4_4",
            data={
                "position": {"x": 1, "y": 2, "z": 3},
                "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
            },
        )

        data = json.loads(camera.json())["data"]
        self.assertEqual(data["position"], {"x": 1, "y": 2, "z": 3})
        self.assertEqual(data["rotation"], {"x": 0, "y": 0, "z": 0, "w": 1})


if __name__ == "__main__":
    unittest.main()
