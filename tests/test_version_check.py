import io
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.modules["paho"] = MagicMock()
sys.modules["paho.mqtt"] = MagicMock()
sys.modules["paho.mqtt.client"] = MagicMock()
sys.modules["deprecated"] = MagicMock()

from arena.utils.settings import Settings
from arena.utils.version import version_check


class TestVersionCheck(unittest.TestCase):
    def setUp(self):
        """Point the version-check cache at a throwaway directory.

        version_check() both reads and writes a persistent cache under
        ~/.arena, so without isolation these tests would depend on (and
        pollute) the developer's real home directory, and the cache written
        by one test would short-circuit the mocked urlopen in the next.
        Each test gets a fresh, empty cache directory instead.
        """
        tmp_home = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_home.cleanup)

        # Settings._arena_user_dir is resolved from Path.home() at import time,
        # so patching HOME alone is not enough - override the attribute too.
        self.enterContext(patch.dict(
            os.environ,
            {"HOME": tmp_home.name, "USERPROFILE": tmp_home.name},
        ))
        self.enterContext(patch.object(
            Settings, "_arena_user_dir", os.path.join(tmp_home.name, ".arena")
        ))

    @patch('arena.utils.version.request.urlopen')
    @patch('arena.utils.version.metadata.version')
    def test_update_available(self, mock_version, mock_urlopen):
        # Setup mocks
        mock_version.return_value = "0.0.1"

        # Mock fetch response
        mock_response = MagicMock()
        mock_response.__enter__.return_value = io.BytesIO(b'{"info": {"version": "9.9.9"}}')
        mock_urlopen.return_value = mock_response

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        version_check()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Update Check: arena-py 9.9.9 is available!", output)

    @patch('arena.utils.version.request.urlopen')
    @patch('arena.utils.version.metadata.version')
    def test_no_update(self, mock_version, mock_urlopen):
        # Setup mocks
        mock_version.return_value = "1.0.0"

        # Mock fetch response
        mock_response = MagicMock()
        mock_response.__enter__.return_value = io.BytesIO(b'{"info": {"version": "1.0.0"}}')
        mock_urlopen.return_value = mock_response

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        version_check()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertNotIn("Update Check", output)

if __name__ == '__main__':
    unittest.main()
