import unittest

from arena.utils.camera import camera_username


class CameraUsernameTest(unittest.TestCase):
    def test_v2_camera_id(self):
        self.assertEqual(camera_username("jdoe_1448081341"), "jdoe")

    def test_v2_username_with_underscores(self):
        self.assertEqual(camera_username("jane_doe_1448081341"), "jane_doe")

    def test_v2_username_starting_with_camera(self):
        self.assertEqual(camera_username("camera_jdoe_1448081341"), "camera_jdoe")

    def test_v1_camera_id(self):
        self.assertEqual(camera_username("camera_1448081341_jdoe"), "jdoe")

    def test_v1_username_with_underscores(self):
        self.assertEqual(camera_username("camera_1448081341_jane_doe"), "jane_doe")
