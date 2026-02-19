import json
import time
from importlib import metadata
from urllib import request

from .settings import Settings


def version_check(package_name="arena-py"):
    """
    Check for the latest version of the package on PyPI.
    """
    def _check():
        try:
            # Check if we have write access to the cache directory (home)
            if not Settings.check_writable():
                return

            check_interval = 86400  # 24 hours

            # Load existing cache
            cache_data = Settings.load_global_settings()

            # Check last check time
            last_check = cache_data.get("version_check", {}).get("last_check", 0)
            if time.time() - last_check < check_interval:
                return

            current_version = metadata.version(package_name)
            pypi_url = f"https://pypi.org/pypi/{package_name}/json"

            req = request.Request(pypi_url)
            with request.urlopen(req, timeout=10) as response:
                data = json.load(response)
                latest_version = data["info"]["version"]

                if current_version != latest_version:
                    print(f"\n\033[93mUpdate Check: {package_name} {latest_version} is available! (Current: {current_version})\033[0m")
                    print(f"\033[93mUpgrade with: pip install --upgrade {package_name}\033[0m\n")

                # Update cache
                if "version_check" not in cache_data:
                    cache_data["version_check"] = {}
                cache_data["version_check"]["last_check"] = time.time()
                Settings.save_global_settings(cache_data)

        except Exception:
            # Silently fail on network errors or other issues to not disrupt usage
            pass

    _check()
