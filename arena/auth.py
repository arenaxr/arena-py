"""
auth.py - Authentication methods for accessing the ARENA.
"""

import datetime
import io
import json
import os
import pickle
import ssl
import sys
import time
import webbrowser
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

import jwt
import requests
from google.auth import jwt as gJWT
from google.auth.transport.requests import AuthorizedSession, Request
from google_auth_oauthlib.flow import InstalledAppFlow

from arena.utils import timer

_gauth_file = ".arena_google_auth"
_mqtt_token_file = ".arena_mqtt_auth"
_arena_user_dir = f"{str(Path.home())}/.arena"
_local_mqtt_path = f"{_mqtt_token_file}"
_rt = None


class JSONObject:
    def __init__(self, dictionary):
        self.__dict__ = dictionary


class ArenaAuth:

    _scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    def __init__(self):
        self._csrftoken = None
        self._mqtt_token = None
        self._id_token = None

    def authenticate_user(self, web_host, headless):
        """
        Begins authentication flow, getting Google auth, opening web browser if
        needed, getting username and state from ARENA server.

        :param str web_host: The hostname of the ARENA webserver.
        :return: Username from arena-account, or None.
        """
        print("Signing in to the ARENA...")
        print(f"1 headless {headless}")
        try:
            # test for valid browser before starting browser-required auth-flow
            webbrowser.get()
        except webbrowser.Error as err:
            headless = True
            print("Console-only environment detected. {0} ".format(err))

        print(f"2 headless {headless}")
        if headless:
            gauth_json = self._get_gauthid_limited(web_host)
        else:
            gauth_json = self._get_gauthid_desktop(web_host)
        gauth = json.loads(gauth_json)
        creds = None
        scene_auth_dir = self._get_scene_auth_path(web_host)
        scene_gauth_path = f"{scene_auth_dir}/{_gauth_file}"

        if not os.path.exists(scene_auth_dir):
            os.makedirs(scene_auth_dir)

        # store the user's access and refresh tokens
        if os.path.exists(scene_gauth_path):
            with open(scene_gauth_path, "rb") as token:
                creds = pickle.load(token)
            session = AuthorizedSession(creds)
            id_claims = gJWT.decode(creds.id_token, verify=False)

            # for reuse, client_id must still match
            if "installed" not in gauth or "client_id" not in gauth["installed"]:
                creds = None
            if id_claims["aud"] != gauth["installed"]["client_id"]:
                creds = None
            if creds:
                print("Using cached Google authentication.")
        # if no credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Requesting refreshed Google authentication.")
                creds.refresh(Request())
                session = AuthorizedSession(creds)
            else:
                print("Requesting new Google authentication.")
                print("3 headless {headless}")
                if headless:
                    # limited input device auth flow for local client
                    device_resp, status = self._get_device_code(
                        client_id=gauth["installed"]["client_id"]
                    )
                    print(device_resp)
                    print(status)
                    # render user code/link and poll for OOB response
                    device = json.loads(device_resp)
                    print(
                        f"1. Use another device to open: {device['verification_url']}"
                    )
                    print(f"2. Enter this code: {device['user_code']}")
                    exp = time.time() + device["expires_in"]
                    # global _rt
                    # _rt = timer.RepeatedTimer(
                    #     device["interval"],
                    #     self._request_google_device_auth,
                    #     exp_time=exp,
                    #     client_id=gauth["installed"]["client_id"],
                    #     client_secret=gauth["installed"]["client_secret"],
                    #     device_code=device["device_code"],
                    # )
                    delay = device["interval"]
                    next_time = time.time() + delay
                    while True:
                        time.sleep(max(0, next_time - time.time()))

                        access_resp, status = self._get_device_access(
                            client_id=gauth["installed"]["client_id"],
                            client_secret=gauth["installed"]["client_secret"],
                            device_code=device["device_code"],
                        )
                        print(access_resp)
                        print(status)
                        if status == 200:
                            # bytes_data = str.encode(access_resp)
                            # buffer = io.BytesIO(bytes_data)
                            # reader = io.BufferedReader(buffer)
                            # # creds = pickle.load(reader)
                            creds = json.loads(
                                access_resp, object_hook=lambda d: JSONObject(d)
                            )
                            session = AuthorizedSession(creds)
                            break

                        # skip tasks if we are behind schedule:
                        next_time += (time.time() - next_time) // delay * delay + delay
                else:
                    # automated browser flow for local client
                    flow = InstalledAppFlow.from_client_config(
                        json.loads(gauth_json), self._scopes
                    )
                    creds = flow.run_local_server(port=0)
                    session = flow.authorized_session()

            with open(scene_gauth_path, "wb") as token:
                # save the credentials for the next run
                pickle.dump(creds, token)
            os.chmod(scene_gauth_path, 0o600)  # set user-only perms.

        username = None
        self._id_token = creds.id_token
        user_info = self._get_user_state(web_host, self._id_token)
        _user_info = json.loads(user_info)
        if "authenticated" in _user_info and "username" in _user_info:
            username = _user_info["username"]
        profile_info = session.get("https://www.googleapis.com/userinfo/v2/me").json()
        if profile_info:
            print(f"Authenticated Google account: {profile_info['email']}")
        return username

    def _request_google_device_auth(
        self, exp_time, client_id, client_secret, device_code
    ):
        now = time.time()
        if now < exp_time:
            print(f"{now} _request_google_device_auth, exp: {exp_time}")
            access_resp, status = self._get_device_access(
                client_id=client_id,
                client_secret=client_secret,
                device_code=device_code,
            )
            access = json.loads(access_resp)
            print(access_resp)
            print(status)
        else:
            global _rt
            _rt.stop()
            print("Device auth request expired.")
            sys.exit("Terminating...")

    def authenticate_scene(self, web_host, realm, scene, username, video=False):
        """End authentication flow, requesting permissions may change by owner
        or admin, for now, get a fresh mqtt_token each time.

        :param str web_host: The hostname of the ARENA webserver.
        :param str realm: The topic realm name.
        :param str scene: The namespace/scene name combination.
        :param str username: The ARENA username for the user.
        :param bool video: If Jitsi video conference is requested.
        :return: username and mqtt_token from arena-account.
        """
        scene_auth_dir = self._get_scene_auth_path(web_host)
        scene_mqtt_path = f"{scene_auth_dir}/{_mqtt_token_file}"

        print("Using remote-authenticated MQTT token.")
        mqtt_json = self._get_mqtt_token(
            web_host, realm, scene, username, self._id_token, video
        )
        # save mqtt_token
        with open(scene_mqtt_path, mode="w") as d:
            d.write(mqtt_json)
        os.chmod(scene_mqtt_path, 0o600)  # set user-only perms.

        self._mqtt_token = json.loads(mqtt_json)
        self._log_token()
        return self._mqtt_token

    def authenticate_device(self, web_host):
        """
        Check for device mqtt_token, ask for a missing one, and save to local memory.
        """
        device_auth_dir = self._get_device_auth_path(web_host)
        device_mqtt_path = f"{device_auth_dir}/{_mqtt_token_file}"
        # check token expiration
        _remove_credentials(device_auth_dir, expire=True)
        # load device token if valid
        if os.path.exists(device_mqtt_path):
            print("Using user long-term device MQTT token.")
            f = open(device_mqtt_path, "r")
            mqtt_json = f.read()
            f.close()
        else:
            if not os.path.exists(device_auth_dir):
                os.makedirs(device_auth_dir)
            print(
                f"Generate a token for this device at https://{web_host}/user/profile"
            )
            mqtt_json = input("Paste auth MQTT full JSON here for this device: ")
            # save mqtt_token
            with open(device_mqtt_path, mode="w") as d:
                d.write(mqtt_json)
            os.chmod(device_mqtt_path, 0o600)  # set user-only perms.

        self._mqtt_token = json.loads(mqtt_json)
        self._log_token()
        return self._mqtt_token

    def has_publish_rights(self, token, topic):
        """Check the MQTT token for permission to publish to topic."""
        tok = jwt.decode(token, options={"verify_signature": False})
        for pub in tok["publ"]:
            if topic.startswith(pub.strip().rstrip("/").rstrip("#")):
                return True
        return False

    def _get_scene_auth_path(self, web_host):
        return f"{_arena_user_dir}/python/{web_host}/s"

    def _get_device_auth_path(self, web_host):
        return f"{_arena_user_dir}/python/{web_host}/d"

    def get_writable_scenes(self, web_host):
        """Request list of scene names for logged in user that user has publish permission for.

        :param str web_host: The hostname of the ARENA webserver.
        :return: list of scenes.
        """
        my_scenes = self._get_my_scenes(web_host, self._id_token)
        return json.loads(my_scenes)

    def _log_token(self):
        """
        Update user with token in use.
        """
        username = None
        if "username" in self._mqtt_token:
            username = self._mqtt_token["username"]
        print(f"ARENA Token Username: {username}")

        now = time.time()
        tok = jwt.decode(self._mqtt_token["token"], options={"verify_signature": False})
        exp = float(tok["exp"])
        delta = exp - now
        dur_str = str(datetime.timedelta(milliseconds=delta * 1000))
        print(f"ARENA Token valid for: {dur_str}h")

    def store_environment_auth(self, username, token):
        """
        Keep a copy of the token in local memory for urlopen and other tasks.
        """
        if username and token:
            print("Using environment MQTT token.")
            self._mqtt_token = {"username": username, "token": token}
            self._log_token()

    def check_local_auth(self):
        """
        Check for local mqtt_token and save to local memory.
        """
        # TODO: remove local check after ARTS supports mqtt_token passing
        # 4 Oct 2021 remove deprecated user home creds path
        _remove_credentials(str(Path.home()))
        # check token expiration
        _remove_credentials(str(Path.cwd()), expire=True)
        # load local token if valid
        if os.path.exists(_local_mqtt_path):
            print("Using local MQTT token.")
            f = open(_local_mqtt_path, "r")
            mqtt_json = f.read()
            f.close()
            self._mqtt_token = json.loads(mqtt_json)
            self._log_token()
            return self._mqtt_token
        return None

    def _get_csrftoken(self, web_host):
        # get the csrftoken for django
        csrf_url = f"https://{web_host}/user/login"
        client = requests.session()
        client.get(csrf_url, verify=self.verify(web_host))  # sets cookie
        if "csrftoken" in client.cookies:
            self._csrftoken = client.cookies["csrftoken"]
        elif "csrf" in client.cookies:
            self._csrftoken = client.cookies["csrf"]
        else:
            self._csrftoken = None
        return self._csrftoken

    def _get_gauthid_desktop(self, web_host):
        url = f"https://{web_host}/conf/gauth.json"
        return self.urlopen(url)

    def _get_gauthid_limited(self, web_host):
        url = f"https://{web_host}/conf/gauth-device.json"
        return self.urlopen(url)

    def _get_device_code(self, client_id):
        url = "https://oauth2.googleapis.com/device/code"
        params = {
            "client_id": client_id,
            "scope": "email profile",
        }
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        body, status = self.urlopen_def(url, data=data)
        return body, status

    def _get_device_access(self, client_id, client_secret, device_code):
        url = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        body, status = self.urlopen_def(url, data=data)
        return body, status

    def _get_my_scenes(self, web_host, id_token):
        url = f"https://{web_host}/user/my_scenes"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": id_token}
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        return self.urlopen(url, data=data, csrf=self._csrftoken)

    def _get_user_state(self, web_host, id_token):
        url = f"https://{web_host}/user/user_state"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": id_token}
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        return self.urlopen(url, data=data, csrf=self._csrftoken)

    def _get_mqtt_token(self, web_host, realm, scene, username, id_token, video):
        url = f"https://{web_host}/user/mqtt_auth"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {
            "id_auth": "google-installed",
            "username": username,
            "id_token": id_token,
            "realm": realm,
            "scene": scene,
        }
        if video:
            params["camid"] = True
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        return self.urlopen(url, data=data, csrf=self._csrftoken)

    def verify(self, web_host):
        return web_host != "localhost"

    def urlopen_def(self, url, data=None):
        """urlopen is for non-ARENA URL connections.
        :param str url: the url to POST/GET.
        :param str data: None for GET, add params for POST.
        """
        res = None
        status = None
        try:
            req = request.Request(url)
            with request.urlopen(req, data=data) as f:
                status = f.status
                res = f.read().decode("utf-8")
        except (
            requests.exceptions.ConnectionError,
            ConnectionError,
            URLError,
            HTTPError,
        ) as err:
            print(f"{err}: {url}")
            status = err.code
            if res is not None:
                print(res)  # show additional errors in response if present
        return res, status

    def urlopen(self, url, data=None, creds=False, csrf=None):
        """urlopen is for ARENA URL connections.
        :param str url: the url to POST/GET.
        :param str data: None for GET, add params for POST.
        :param bool creds: True to pass the MQTT token as a cookie.
        :param str csrf: The csrftoken.
        """
        urlparts = urlsplit(url)
        res = None
        try:
            req = request.Request(url)
            if creds:
                req.add_header("Cookie", f"mqtt_token={self._mqtt_token['token']}")
            if csrf:
                req.add_header("Cookie", f"csrftoken={csrf}")
                req.add_header("X-CSRFToken", csrf)
            if self.verify(urlparts.netloc):
                with request.urlopen(req, data=data) as f:
                    res = f.read().decode("utf-8")
            else:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with request.urlopen(req, data=data, context=context) as f:
                    res = f.read().decode("utf-8")
            return res
        except (
            requests.exceptions.ConnectionError,
            ConnectionError,
            URLError,
            HTTPError,
        ) as err:
            print(f"{err}: {url}")
            if res is not None:
                print(res)  # show additional errors in response if present
            if isinstance(err, HTTPError) and err.code in (401, 403):
                # user not authorized on website yet, they don"t have an ARENA username
                us = urlsplit(url)
                base_url = f"{us.scheme}://{us.netloc}"
                print(f"Do you have a valid ARENA account on {base_url}?")
                print(f"Create an account in a web browser at: {base_url}/user")
            sys.exit("Terminating...")


def signout():
    auth_files = [_mqtt_token_file, _gauth_file]
    for root, dirs, files in os.walk(_arena_user_dir):
        if any(map(lambda v: v in auth_files, files)):
            _remove_credentials(root)
    if os.path.exists(_local_mqtt_path):
        _remove_credentials(_local_mqtt_path)
    print("Signed out of the ARENA.")


def _print_mqtt_token(storage_str, mqtt_claims):
    print("\nARENA MQTT/Video Permissions")
    print("----------------------")
    exp_str = time.strftime("%c", time.localtime(mqtt_claims["exp"]))
    print(f"Expires: {exp_str}")
    print(f"Storage: {storage_str}")
    print(f"{json.dumps(mqtt_claims, indent=4)}")


def permissions():
    mqtt_claims = None
    # env storage auth
    if os.environ.get("ARENA_USERNAME") and os.environ.get("ARENA_PASSWORD"):
        mqtt_token = os.environ["ARENA_PASSWORD"]
        mqtt_claims = jwt.decode(
            mqtt_token["token"], options={"verify_signature": False}
        )
        _print_mqtt_token("environment variable 'ARENA_PASSWORD'", mqtt_claims)
    # file storage auth
    token_paths = []
    for root, dirs, files in os.walk(_arena_user_dir):
        if _mqtt_token_file in files:
            token_paths.append(os.path.join(root, _mqtt_token_file))
    if os.path.exists(_local_mqtt_path):
        token_paths.append(_local_mqtt_path)
    for mqtt_path in token_paths:
        f = open(mqtt_path, "r")
        mqtt_json = f.read()
        f.close()
        try:
            mqtt_token = json.loads(mqtt_json)
        except json.decoder.JSONDecodeError as err:
            print(f"{err}, {mqtt_path}")
            continue
        mqtt_claims = jwt.decode(
            mqtt_token["token"], options={"verify_signature": False}
        )
        _print_mqtt_token(mqtt_path, mqtt_claims)
    # no permissions
    if not mqtt_claims:
        print("Not signed into the ARENA.")


def _remove_credentials(cred_dir, expire=False):
    """
    Helper to remove credentials in path with expiration option.
    """
    test_gauth_path = f"{cred_dir}/{_gauth_file}"
    test_mqtt_path = f"{cred_dir}/{_mqtt_token_file}"
    if os.path.exists(test_mqtt_path):
        f = open(test_mqtt_path, "r")
        mqtt_json = f.read()
        f.close()
        try:
            mqtt_token = json.loads(mqtt_json)
        except json.decoder.JSONDecodeError as err:
            print(f"{err}, {test_mqtt_path}")
            os.remove(test_mqtt_path)
            return
        try:
            mqtt_claims = jwt.decode(
                mqtt_token["token"], options={"verify_signature": False}
            )
        except Exception as err:
            print(f"{err}, {test_mqtt_path}")
            os.remove(test_mqtt_path)
            return

        exp = float(mqtt_claims["exp"])
        now = time.time()
        if expire and now < exp:
            return  # exit if expire request is still good
        # otherwise remove
        os.remove(test_mqtt_path)
    if os.path.exists(test_gauth_path):
        os.remove(test_gauth_path)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
