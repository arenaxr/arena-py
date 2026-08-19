"""Tests that the scene's local user/hand back-references stay out of json().

Scene._process_message links a hand and its user in both directions:

    user.hands[object_type] = obj
    obj.camera = user

That is a genuine reference cycle. Object.json_preprocess strips the other
local-only attributes it maintains (evt_handler, update_handler, animations,
delayed_prop_tasks, _private_userid) but did not strip these two, so both ends
survived into the payload and json.dumps raised "Circular reference detected"
from either side of the pair.

Neither key has any place on the wire in the first place: they are handler
conveniences the library maintains locally, and the server identifies a hand's
user through data.dep, which these tests also pin as unaffected. Objects that
are not cameras or hands never carried either key, so their payloads are
unchanged -- test_normal_object_payload_is_unchanged is what holds that down.

Object.all_objects is global class state, so each test clears it either side of
itself.
"""

import json
import unittest

from arena.objects import Box, Camera, HandLeft, HandRight, Object


def make_camera(object_id="camera_test_test"):
    """Builds a Camera from a data dict, the way Scene does."""
    return Camera(object_id=object_id, data={"position": {"x": 0, "y": 1.6, "z": 0}})


def make_linked_hand(camera, hand_class=HandLeft, object_id="handLeft_test_test"):
    """Joins a hand to a camera exactly as Scene._process_message joins them."""
    hand = hand_class(
        object_id=object_id,
        data={"position": {"x": 0, "y": 1, "z": 0}, "dep": camera.object_id},
    )
    camera.hands[hand.object_type] = hand
    hand.camera = camera
    return hand


class LocalBackReferenceTestCase(unittest.TestCase):
    def setUp(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def tearDown(self):
        Object.all_objects.clear()
        Object.private_objects.clear()

    def test_linked_hand_can_be_serialized(self):
        """The cycle used to raise ValueError: Circular reference detected."""
        hand = make_linked_hand(make_camera())

        payload = json.loads(hand.json())

        self.assertEqual(payload["object_id"], "handLeft_test_test")

    def test_linked_camera_can_be_serialized(self):
        """The cycle is symmetric, so the camera side has to work too."""
        camera = make_camera()
        make_linked_hand(camera)

        payload = json.loads(camera.json())

        self.assertEqual(payload["object_id"], "camera_test_test")

    def test_both_hands_linked(self):
        """A user with two hands is the normal case, not a special one."""
        camera = make_camera()
        left = make_linked_hand(camera, HandLeft, "handLeft_test_test")
        right = make_linked_hand(camera, HandRight, "handRight_test_test")

        for obj in (camera, left, right):
            with self.subTest(object_id=obj.object_id):
                self.assertNotIn("camera", json.loads(obj.json()))
                self.assertNotIn("hands", json.loads(obj.json()))

    def test_hand_payload_omits_camera(self):
        """camera is a local reference; it is never sent, cycle or not."""
        hand = make_linked_hand(make_camera())

        self.assertNotIn("camera", json.loads(hand.json()))

    def test_unlinked_hand_payload_omits_camera(self):
        """A hand nobody linked carries camera = None; that is not sent either."""
        hand = HandLeft(object_id="handLeft_9_9", data={"position": {"x": 0, "y": 1, "z": 0}})

        self.assertIsNone(hand.camera)
        self.assertNotIn("camera", json.loads(hand.json()))

    def test_camera_payload_omits_hands(self):
        """hands is a local dict of references; it is never sent."""
        camera = make_camera()
        make_linked_hand(camera)

        self.assertNotIn("hands", json.loads(camera.json()))

    def test_unlinked_camera_payload_omits_hands(self):
        """A user with no hands carries hands = {}; that is not sent either."""
        self.assertNotIn("hands", json.loads(make_camera().json()))

    def test_dep_still_identifies_the_user(self):
        """The server pairs a hand with its user through data.dep, not camera."""
        camera = make_camera()
        hand = make_linked_hand(camera)

        payload = json.loads(hand.json())

        self.assertEqual(payload["data"]["dep"], "camera_test_test")

    def test_local_references_survive_serialization(self):
        """Skipping the keys must not remove them from the object itself.

        Scene reads user.hands and obj.camera after publishing, so json() has to
        leave the live attributes alone.
        """
        camera = make_camera()
        hand = make_linked_hand(camera)

        hand.json()
        camera.json()

        self.assertIs(hand.camera, camera)
        self.assertIs(camera.hands["handLeft"], hand)

    def test_normal_object_payload_is_unchanged(self):
        """An object that is not a camera or a hand is unaffected.

        Neither key ever existed on one, so nothing can be dropped from it.
        """
        box = Box(object_id="plain_box", position=(1, 2, 3))

        payload = json.loads(box.json())

        self.assertEqual(
            payload,
            {
                "object_id": "plain_box",
                "persist": False,
                "type": "object",
                "data": {
                    "object_type": "box",
                    "position": {"x": 1, "y": 2, "z": 3},
                    "rotation": {"x": 0, "y": 0, "z": 0, "w": 1.0},
                    "scale": {"x": 1, "y": 1, "z": 1},
                },
            },
        )

    def test_a_camera_attribute_on_a_plain_object_is_still_skipped(self):
        """The key is skipped by name, so nothing can reintroduce the cycle.

        A handler that hangs a user off an arbitrary object builds the same cycle
        the scene builds for hands, and it has to serialize the same way.
        """
        camera = make_camera()
        box = Box(object_id="attached_box", position=(0, 0, 0))
        box.camera = camera
        camera.hands["handLeft"] = box

        self.assertNotIn("camera", json.loads(box.json()))


if __name__ == "__main__":
    unittest.main()
