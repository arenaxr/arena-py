"""
auth.py - Authentication methods for accessing the ARENA.
"""

import datetime
import json
import os
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
from google_auth_oauthlib.flow import InstalledAppFlow

_gauth_file = ".arena_google_auth"
_mqtt_token_file = ".arena_mqtt_auth"
_arena_user_dir = f"{str(Path.home())}/.arena"
_local_mqtt_path = f"{_mqtt_token_file}"


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
        try:
            # test for valid browser before starting browser-required auth-flow
            webbrowser.get()
        except webbrowser.Error as err:
            headless = True
            print(f"Console-only environment detected. {err} ")

        if headless:
            gauth_json = self._get_gauthid_limited(web_host)
        else:
            gauth_json = self._get_gauthid_desktop(web_host)
        gauth = json.loads(gauth_json)
        if "installed" not in gauth or "client_id" not in gauth["installed"]:
            return None
        creds = None
        refresh_token = None
        scene_auth_dir = self._get_scene_auth_path(web_host)
        scene_gauth_path = f"{scene_auth_dir}/{_gauth_file}"

        if not os.path.exists(scene_auth_dir):
            os.makedirs(scene_auth_dir)

        # store the user's access and refresh tokens
        if os.path.exists(scene_gauth_path):
            try:
                with open(scene_gauth_path, "r", encoding="utf-8") as token:
                    creds = json.load(token)
            except (json.JSONDecodeError, UnicodeDecodeError):
                creds = None  # bad/old storage format

            if creds:
                # for reuse, client_id must still match
                id_claims = gJWT.decode(creds["id_token"], verify=False)
                if id_claims["aud"] != gauth["installed"]["client_id"]:
                    creds = None  # switched auth systems
            if id_claims["exp"]:
                exp = float(id_claims["exp"])
                if exp <= time.time():
                    refresh_token = creds["refresh_token"]
                    creds = None  # expired token

        if creds:
            print("Using cached Google authentication.")
        else:
            if refresh_token:
                print("Requesting refreshed Google authentication.")
                creds_jstr = self._run_gauth_token_refresh(
                    client_id=gauth["installed"]["client_id"],
                    client_secret=gauth["installed"]["client_secret"],
                    refresh_token=refresh_token,
                )
                creds = json.loads(creds_jstr)
            else:
                # if no credentials available, let the user log in.
                if headless:
                    # limited input device auth flow for local client
                    print("Requesting new device Google authentication.")
                    creds_jstr = self._run_gauth_device_flow(
                        client_id=gauth["installed"]["client_id"],
                        client_secret=gauth["installed"]["client_secret"],
                    )
                    creds = json.loads(creds_jstr)
                else:
                    # automated browser flow for local client
                    print("Requesting new browser Google authentication.")
                    flow = InstalledAppFlow.from_client_config(json.loads(gauth_json), self._scopes)
                    credentials = flow.run_local_server(port=0)
                    creds_jstr = credentials.to_json()
                    creds = json.loads(creds_jstr)
                    creds["id_token"] = credentials.id_token

            with open(scene_gauth_path, "w", encoding="utf-8") as token:
                # save the credentials for the next run
                json.dump(creds, token)
            os.chmod(scene_gauth_path, 0o600)  # set user-only perms.

        username = None
        self._id_token = creds["id_token"]
        user_info = self._get_user_state(web_host, self._id_token)
        _user_info = json.loads(user_info)
        if "authenticated" in _user_info and "username" in _user_info:
            username = _user_info["username"]
        id_claims = gJWT.decode(creds["id_token"], verify=False)
        print(f"Authenticated Google account: {id_claims['email']}")
        return username

    def _run_gauth_token_refresh(self, client_id, client_secret, refresh_token):
        refresh_resp, status, url = self._get_gauth_refresh_token(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )
        if 200 <= status <= 299:  # success
            return refresh_resp
        else:  # error
            print(f"HTTP error {status}: {url}\n{refresh_resp}")
            sys.exit("Terminating...")

    def _run_gauth_device_flow(self, client_id, client_secret):
        device_resp, status, url = self._get_gauth_device_code(client_id=client_id)
        if 200 > status > 299:  # error
            print(f"HTTP error {status}: {url}\n{device_resp}")
            sys.exit("Terminating...")
        # render user code/link and poll for OOB response
        device = json.loads(device_resp)
        print(f"1. Go to this page on any device: {device['verification_url']}")
        print(f"2. Enter this code on that page: {device['user_code']}")
        exp = time.time() + device["expires_in"]
        delay = device["interval"]

        next_time = time.time() + delay
        while True:
            time.sleep(max(0, next_time - time.time()))

            if time.time() > exp:
                print(f"Device auth request expired after {delay/60} minutes.")
                sys.exit("Terminating...")

            access_resp, status, url = self._get_gauth_device_token(
                client_id=client_id,
                client_secret=client_secret,
                device_code=device["device_code"],
            )
            if 200 <= status <= 299:  # success
                return access_resp
            if status == 428:  # awaiting remote user code and approval
                # skip tasks if we are behind schedule:
                next_time += (time.time() - next_time) // delay * delay + delay
            else:  # error
                print(f"HTTP error {status}: {url}\n{access_resp}")
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
        mqtt_json = self._get_mqtt_token(web_host, realm, scene, username, self._id_token, video)
        # save mqtt_token
        with open(scene_mqtt_path, "w", encoding="utf-8") as d:
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
            print(f"Generate a token for this device at https://{web_host}/user/profile")
            mqtt_json = input("Paste auth MQTT full JSON here for this device: ")
            # save mqtt_token
            with open(device_mqtt_path, "w", encoding="utf-8") as d:
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

    def _encode_params(self, params):
        query_string = parse.urlencode(params)
        data = query_string.encode("ascii")
        return data

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

    def _get_gauth_device_code(self, client_id):
        url = "https://oauth2.googleapis.com/device/code"
        params = {
            "client_id": client_id,
            "scope": "email profile",
        }
        body, status = self.urlopen_def(url, data=self._encode_params(params))
        return body, status, url

    def _get_gauth_device_token(self, client_id, client_secret, device_code):
        url = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        body, status = self.urlopen_def(url, data=self._encode_params(params))
        return body, status, url

    def _get_gauth_refresh_token(self, client_id, client_secret, refresh_token):
        url = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        body, status = self.urlopen_def(url, data=self._encode_params(params))
        return body, status, url

    def _get_my_scenes(self, web_host, id_token):
        url = f"https://{web_host}/user/my_scenes"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": id_token}
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def _get_user_state(self, web_host, id_token):
        url = f"https://{web_host}/user/user_state"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": id_token}
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

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
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def verify(self, web_host):
        return web_host != "localhost"

    def urlopen_def(self, url, data=None):
        """urlopen default is for non-ARENA URL connections.
        :param str url: the url to POST/GET.
        :param str data: None for GET, add params for POST.
        """
        body, status = None, None
        try:
            req = request.Request(url)
            with request.urlopen(req, data=data) as f:
                status = f.status
                body = f.read().decode("utf-8")
        except HTTPError as err:
            # do not log errors, allow consumer to decide
            status = err.code
            body = err.read().decode("utf-8")
        except (
            requests.exceptions.ConnectionError,
            ConnectionError,
            URLError,
        ) as err:
            print(f"{err}: {url}")

        return body, status

    def urlopen(self, url, data=None, creds=False, csrf=None):
        """urlopen is for ARENA URL connections.
        :param str url: the url to POST/GET.
        :param str data: None for GET, add params for POST.
        :param bool creds: True to pass the MQTT token as a cookie.
        :param str csrf: The csrftoken.
        """
        urlparts = urlsplit(url)
        body = None
        try:
            req = request.Request(url)
            if creds:
                req.add_header("Cookie", f"mqtt_token={self._mqtt_token['token']}")
            if csrf:
                req.add_header("Cookie", f"csrftoken={csrf}")
                req.add_header("X-CSRFToken", csrf)
            if self.verify(urlparts.netloc):
                with request.urlopen(req, data=data) as f:
                    body = f.read().decode("utf-8")
            else:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with request.urlopen(req, data=data, context=context) as f:
                    body = f.read().decode("utf-8")
            return body
        except HTTPError as err:
            print(f"{err}: {url}")
            print(err.read().decode("utf-8"))  # show additional errors in response if present
            if err.code in (401, 403):
                # user not authorized on website yet, they don"t have an ARENA username
                us = urlsplit(url)
                base_url = f"{us.scheme}://{us.netloc}"
                print(f"Do you have a valid ARENA account on {base_url}?")
                print(f"Create an account in a web browser at: {base_url}/user")
            sys.exit("Terminating...")
        except (
            requests.exceptions.ConnectionError,
            ConnectionError,
            URLError,
        ) as err:
            print(f"{err}: {url}")
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
        mqtt_claims = jwt.decode(mqtt_token["token"], options={"verify_signature": False})
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
        mqtt_claims = jwt.decode(mqtt_token["token"], options={"verify_signature": False})
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
            mqtt_claims = jwt.decode(mqtt_token["token"], options={"verify_signature": False})
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
