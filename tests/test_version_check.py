import io
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.modules["paho"] = MagicMock()
sys.modules["paho.mqtt"] = MagicMock()
sys.modules["paho.mqtt.client"] = MagicMock()
sys.modules["deprecated"] = MagicMock()

from arena.utils.version import version_check


class TestVersionCheck(unittest.TestCase):
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
