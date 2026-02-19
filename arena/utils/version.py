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
            if "version_check" not in cache_data:
                cache_data["version_check"] = {}

            last_check = cache_data["version_check"].get("last_check", 0)
            cached_latest = cache_data["version_check"].get("latest_version")
            current_version = metadata.version(package_name)

            # Perform online check if interval passed
            if time.time() - last_check > check_interval:
                try:
                    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
                    req = request.Request(pypi_url)
                    with request.urlopen(req, timeout=10) as response:
                        data = json.load(response)
                        cached_latest = data["info"]["version"]

                        # Update cache
                        cache_data["version_check"]["last_check"] = time.time()
                        cache_data["version_check"]["latest_version"] = cached_latest
                        Settings.save_global_settings(cache_data)
                except Exception:
                    # If online check fails, just proceed with whatever we have cached
                    pass

            # Warn if we have a known latest version that is newer than current
            if cached_latest and cached_latest != current_version:
                print(f"\n\033[93mUpdate Check: {package_name} {cached_latest} is available! (Current: {current_version})\033[0m")
                print(f"\033[93mUpgrade with: pip install --upgrade {package_name}\033[0m\n")

        except Exception:
            # Silently fail on other issues to not disrupt usage
            pass

    _check()
