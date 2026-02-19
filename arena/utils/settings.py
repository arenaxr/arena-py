import os
import json
from pathlib import Path

class Settings:
    _arena_user_dir = os.path.join(str(Path.home()), ".arena")
    _gauth_file = ".arena_google_auth"
    _mqtt_token_file = ".arena_mqtt_auth"
    _version_check_file = ".arena_package_settings"

    @classmethod
    def get_arena_user_dir(cls):
        return cls._arena_user_dir

    @classmethod
    def _get_auth_path(cls, web_host, type):
        # type is 's' for scene or 'd' for device
        return os.path.join(cls._arena_user_dir, "python", web_host, type)

    @classmethod
    def get_scene_auth_path(cls, web_host):
        return cls._get_auth_path(web_host, "s")

    @classmethod
    def get_device_auth_path(cls, web_host):
        return cls._get_auth_path(web_host, "d")

    @classmethod
    def load_json_file(cls, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    @classmethod
    def save_json_file(cls, path, data, mode=None):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            if mode:
                os.chmod(path, mode)
        except OSError:
            pass

    @classmethod
    def get_global_settings_path(cls):
        return os.path.join(cls._arena_user_dir, "python", cls._version_check_file)

    @classmethod
    def load_global_settings(cls):
        return cls.load_json_file(cls.get_global_settings_path())

    @classmethod
    def save_global_settings(cls, data):
        cls.save_json_file(cls.get_global_settings_path(), data)

    @classmethod
    def check_writable(cls):
        """Checks if the user home directory is writable."""
        return os.access(os.path.expanduser("~"), os.W_OK)
