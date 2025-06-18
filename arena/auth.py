"""
auth.py - Authentication methods for accessing the ARENA.
"""

import base64
import binascii
import datetime
import json
import os
import re
import secrets
import ssl
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlsplit

from .utils import topic_matches_sub

_gauth_file = ".arena_google_auth"
_mqtt_token_file = ".arena_mqtt_auth"
_arena_user_dir = f"{str(Path.home())}/.arena"
_local_mqtt_path = f"{_mqtt_token_file}"
_auth_callback_hostname = "localhost"
_auth_callback_server = None
_auth_state_code = None
_auth_response_code = None
_scopes = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]


class ArenaAuth:

    def __init__(self):
        self._csrftoken = None
        self._mqtt_token = None
        self._id_token = None
        self._user_info = None
        self._store_token = None

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

            if creds and "id_token" in creds:
                id_claims = _jwt_decode(creds["id_token"])
                # for reuse, client_id must still match
                if id_claims["aud"] != gauth["installed"]["client_id"]:
                    creds = None  # switched auth systems
            if creds and "refresh_token" in creds:
                refresh_token = creds["refresh_token"]
            if creds and id_claims:
                exp = float(id_claims["exp"])
                if exp <= time.time():
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
            else:
                # if no credentials available, let the user log in.
                if headless:
                    # limited input device auth flow for local client
                    print("Requesting new device Google authentication.")
                    creds_jstr = self._run_gauth_device_flow(
                        client_id=gauth["installed"]["client_id"],
                        client_secret=gauth["installed"]["client_secret"],
                    )
                else:
                    # automated browser flow for local client
                    print("Requesting new browser Google authentication.")
                    creds_jstr = self._run_gauth_installed_flow(
                        client_id=gauth["installed"]["client_id"],
                        client_secret=gauth["installed"]["client_secret"],
                    )

            creds = json.loads(creds_jstr)
            with open(scene_gauth_path, "w", encoding="utf-8") as token:
                # save the credentials for the next run
                json.dump(creds, token)
            os.chmod(scene_gauth_path, 0o600)  # set user-only perms.

        username = None
        self._id_token = creds["id_token"]
        user_info = self._get_user_state(web_host)
        self._user_info = json.loads(user_info)
        if "authenticated" in self._user_info and "username" in self._user_info:
            username = self._user_info["username"]
        id_claims = _jwt_decode(creds["id_token"])
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

    def _run_gauth_installed_flow(self, client_id, client_secret):
        global _auth_callback_server, _auth_response_code, _auth_state_code
        # start server listener
        _auth_callback_server = HTTPServer((_auth_callback_hostname, 0), OAuthCallbackServer)
        port = _auth_callback_server.server_address[1]
        _auth_state_code = secrets.token_urlsafe(16)
        browser_auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri=http://{_auth_callback_hostname}:{port}/&scope={'+'.join(_scopes)}&state={_auth_state_code}&access_type=offline"
        print(f"Please visit this URL to authorize ARENA-py: {browser_auth_url}")

        # launch web oauth flow
        webbrowser.open(browser_auth_url, new=2, autoraise=True)
        try:
            _auth_callback_server.serve_forever()
        except KeyboardInterrupt:
            pass

        # synchronous wait for auth
        access_resp, status, url = self._get_gauth_installed_token(
            client_id=client_id,
            client_secret=client_secret,
            auth_code=_auth_response_code,
            # redirect_uri=_auth_response_code,
        )
        if 200 <= status <= 299:  # success
            return access_resp
        else:  # error
            print(f"HTTP error {status}: {url}\n{access_resp}")
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

    def authenticate_scene(self, web_host, realm, scene, username, video=False, env=False):
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
        mqtt_json = self._get_mqtt_token(web_host, realm, scene, username, video, env)
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
            with open(device_mqtt_path, "r", encoding="utf8") as f:
                mqtt_json = f.read()
        else:
            if not os.path.exists(device_auth_dir):
                os.makedirs(device_auth_dir)
            print(f"Generate a token for this device at https://{web_host}/user/v2/profile")
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
        tok = _jwt_decode(token)
        for pub in tok["publ"]:
            if topic_matches_sub(pub.strip(), topic):
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
        my_scenes = self._get_my_scenes(web_host)
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
        tok = _jwt_decode(self._mqtt_token["token"])
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
            with open(_local_mqtt_path, "r", encoding="utf8") as f:
                mqtt_json = f.read()
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
        csrf_url = f"https://{web_host}/user/v2/login"
        self.urlopen(csrf_url)
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

    def _get_gauth_installed_token(self, client_id, client_secret, auth_code, redirect_uri=None):
        url = "https://oauth2.googleapis.com/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            # "redirect_uri": redirect_uri,
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

    def _confirm_gauth(self):
        if not self._id_token:
            raise IOError(
                "Google auth is required. Remove manual .arena_mqtt_token or env ARENA_PASSWORD. Headless auth options are available using `scene=Scene(..., headless=True).`"
            )

    def _get_my_scenes(self, web_host):
        self._confirm_gauth()
        url = f"https://{web_host}/user/v2/my_scenes"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": self._id_token}
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def _get_user_state(self, web_host):
        self._confirm_gauth()
        url = f"https://{web_host}/user/v2/user_state"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": self._id_token}
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def _get_store_login(self, web_host):
        self._confirm_gauth()
        url = f"https://{web_host}/user/v2/storelogin"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {"id_token": self._id_token}
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def upload_store_file(self, web_host, scenename, src_file_path, dest_file_path=None):
        """Upload a source file to the user's file store space. Google authentication is required.

        :param str web_host: The hostname of the ARENA webserver.
        :param str scenename: The scene name/id.
        :param str src_file_path: Local path to the file to upload (required).
        :param str dest_file_path: Destination file path, can include dirs. Defaults to filename from src_file_path (optional).
        :return str: Url address of successful file upload location, or None if failed.
        """
        self._confirm_gauth()
        # request FS login if this is the first time.
        if not self._store_token:
            self._get_store_login(web_host)
            if not self._store_token:
                raise IOError("Filestore login failed!")

        # send file to filestore
        if not dest_file_path:
            dest_file_path = Path(src_file_path).name
        safe_file_path = re.sub(r"/(\W+)/gi", "-", dest_file_path)
        if self._user_info["is_staff"]:
            store_res_prefix = f"users/{self._user_info['username']}/"
        else:
            store_res_prefix = ""
        user_file_path = f"scenes/{scenename}/{safe_file_path}"
        store_res_path = f"{store_res_prefix}{user_file_path}"
        store_ext_path = f"store/users/{self._user_info['username']}/{user_file_path}"
        url = f"https://{web_host}/storemng/api/resources/{store_res_path}?override=true"
        headers = {
            "Content-Length": os.stat(src_file_path).st_size,
            "X-Auth": self._store_token,
        }
        print(f"Uploading {src_file_path}....")
        with open(src_file_path, "rb") as f:
            body = self.urlopen(url, data=f, headers=headers)
        if body:
            print("Upload DONE!")
            return f"https://{web_host}/{store_ext_path}"
        else:
            raise IOError(f"Filestore upload failed! Dest: {dest_file_path}")

    def _get_mqtt_token(self, web_host, realm, scene, username, video, env):
        self._confirm_gauth()
        url = f"https://{web_host}/user/v2/mqtt_auth"
        if not self._csrftoken:
            self._csrftoken = self._get_csrftoken(web_host)
        params = {
            "id_auth": "google-installed",
            "username": username,
            "id_token": self._id_token,
            "client": "py",
            "realm": realm,
            "scene": scene,
            "userid": "true",
        }
        if video:
            params["camid"] = "true"
        if env:
            params["environmentid"] = "true"
        return self.urlopen(url, data=self._encode_params(params), csrf=self._csrftoken)

    def verify(self, web_host):
        return web_host != "localhost" and not web_host.endswith(".local")

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
            ConnectionError,
            URLError,
        ) as err:
            print(f"{err}: {url}")

        return body, status

    def urlopen(self, url, data=None, headers=None, creds=False, csrf=None):
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
            if headers:
                for k in headers:
                    req.add_header(k, headers[k])
            if self.verify(urlparts.netloc):
                with request.urlopen(req, data=data) as f:
                    body = f.read().decode("utf-8")
                    cookies = f.info().get_all("Set-Cookie")
            else:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with request.urlopen(req, data=data, context=context) as f:
                    body = f.read().decode("utf-8")
                    cookies = f.info().get_all("Set-Cookie")
            if cookies:
                for cookie in cookies:
                    if "auth=" in cookie:
                        for m in re.finditer(r"(^| )auth=([^;]+)", cookie):
                            self._store_token = m.group(2)
                    if "csrftoken=" in cookie:
                        for m in re.finditer(r"(^| )csrftoken=([^;]+)", cookie):
                            self._csrftoken = m.group(2)
                    elif "csrf=" in cookie:
                        for m in re.finditer(r"(^| )csrf=([^;]+)", cookie):
                            self._csrftoken = m.group(2)
            return body
        except HTTPError as err:
            print(f"{err}: {url}")
            body = err.read().decode("utf-8")
            if "<!doctype html>" not in body.lower():
                print(body)  # show additional errors in response if present
            if err.code in (401, 403):
                # user not authorized on website yet, they don"t have an ARENA username
                us = urlsplit(url)
                base_url = f"{us.scheme}://{us.netloc}"
                print(f"Do you have a valid ARENA account on {base_url}?")
                print(f"Create an account in a web browser at: {base_url}/user")
            sys.exit("Terminating...")
        except (
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
        mqtt_claims = _jwt_decode(mqtt_token["token"])
        _print_mqtt_token("environment variable 'ARENA_PASSWORD'", mqtt_claims)
    # file storage auth
    token_paths = []
    for root, dirs, files in os.walk(_arena_user_dir):
        if _mqtt_token_file in files:
            token_paths.append(os.path.join(root, _mqtt_token_file))
    if os.path.exists(_local_mqtt_path):
        token_paths.append(_local_mqtt_path)
    for mqtt_path in token_paths:
        with open(mqtt_path, "r", encoding="utf8") as f:
            mqtt_json = f.read()
        try:
            mqtt_token = json.loads(mqtt_json)
        except json.decoder.JSONDecodeError as err:
            print(f"{err}, {mqtt_path}")
            continue
        mqtt_claims = _jwt_decode(mqtt_token["token"])
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
        with open(test_mqtt_path, "r", encoding="utf8") as f:
            mqtt_json = f.read()
        try:
            mqtt_token = json.loads(mqtt_json)
        except json.decoder.JSONDecodeError as err:
            print(f"{err}, {test_mqtt_path}")
            os.remove(test_mqtt_path)
            return
        try:
            mqtt_claims = _jwt_decode(mqtt_token["token"])
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


# Adapted from https://github.com/u-clarkdeveloper/simple-jwt/blob/main/src/simple_jwt/jwt.py
def _jwt_decode(token):
    try:
        _, claims, _ = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid JWT: token must have 3 parts separated by '.'") from exc

    # Add padding to make the base64 string length a multiple of 4
    def add_padding(s):
        return s + "=" * (4 - len(s) % 4) if len(s) % 4 else s

    try:
        claims_decoded = base64.urlsafe_b64decode(add_padding(claims))
    except Exception as exc:
        raise binascii.Error("Invalid JWT: token must be base64url encoded") from exc

    try:
        claims_data = json.loads(claims_decoded)
    except json.JSONDecodeError:
        print("Invalid JWT: token must be json encoded")

    return claims_data


class OAuthCallbackServer(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global _auth_callback_server, _auth_response_code, _auth_state_code
        parsed_path = urlparse(self.path)
        params = parse.parse_qs(parsed_path.query)
        if "code" in params:
            if params["state"] != _auth_state_code:
                msg = "ARENA-py authorization flow error: Invalid state response."
            if params["scope"] != '+'.join(_scopes):
                msg = "ARENA-py authorization flow error: Invalid scopes response."
            _auth_response_code = params["code"]
            msg = "ARENA-py authorization flow is complete. You may close this window."
        elif "error" in params:
            msg = f"ARENA-py authorization flow error: {params['error']}"
        else:
            msg = "ARENA-py authorization flow error: Expected parameters not received."

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(msg, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        _auth_callback_server.server_close()


if __name__ == "__main__":
    globals()[sys.argv[1]]()
