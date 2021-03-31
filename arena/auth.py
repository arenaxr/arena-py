"""
auth.py - Authentication methods for accessing the ARENA.
"""

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
from google.auth.transport.requests import AuthorizedSession, Request
from google_auth_oauthlib.flow import InstalledAppFlow

debug_toggle = False
_scopes = ["openid",
           "https://www.googleapis.com/auth/userinfo.profile",
           "https://www.googleapis.com/auth/userinfo.email"]
_user_gauth_path = f'{str(Path.home())}/.arena_google_auth'
_user_mqtt_path = f'{str(Path.home())}/.arena_mqtt_auth'
_local_mqtt_path = f'.arena_mqtt_auth'
_csrftoken = None
_mqtt_token = None
_id_token = None


def authenticate_user(host, debug=False):
    """
    Begins authentication flow, getting Google auth, opening web browser if
    needed, getting username and state from ARENA server.
    host: The hostname of the ARENA webserver.
    debug: True to skip SSL verify for localhost tests.
    Returns: Username from arena-account, or None.
    """
    global debug_toggle
    global _id_token
    debug_toggle = debug
    print("Signing in to the ARENA...")

    local_token = _local_token_check()
    if local_token:
        return local_token["username"]

    creds = None
    browser = None
    try:
        browser = webbrowser.get()
    except (webbrowser.Error) as err:
        print("Console-only login. {0}".format(err))

    # store the user's access and refresh tokens
    if os.path.exists(_user_gauth_path):
        print("Using cached Google authentication.")
        with open(_user_gauth_path, 'rb') as token:
            creds = pickle.load(token)
        session = AuthorizedSession(creds)
    # if no credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Requesting refreshed Google authentication.")
            creds.refresh(Request())
            session = AuthorizedSession(creds)
        else:
            print("Requesting new Google authentication.")
            gauth_json = _get_gauthid(host)
            flow = InstalledAppFlow.from_client_config(
                json.loads(gauth_json), _scopes)
            if browser:
                # TODO: select best client port to avoid likely conflicts
                creds = flow.run_local_server(port=8989)
            else:
                creds = flow.run_console()
            session = flow.authorized_session()
        with open(_user_gauth_path, 'wb') as token:
            # save the credentials for the next run
            pickle.dump(creds, token)
        os.chmod(_user_gauth_path, 0o600)  # set user-only perms.

    username = None
    _id_token = creds.id_token
    user_info = _get_user_state(host, _id_token)
    _user_info = json.loads(user_info)
    if 'authenticated' in _user_info and 'username' in _user_info:
        username = _user_info["username"]
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    if profile_info:
        print(f'Authenticated Google account: {profile_info["email"]}')
    return username


def authenticate_scene(host, realm, scene, username, debug=False):
    """ End authentication flow, requesting permissions may change by owner
    or admin, for now, get a fresh mqtt_token each time.
    host: The hostname of the ARENA webserver.
    realm: The topic realm name.
    scene: The namespace/scene name combination.
    username: The ARENA username for the user.
    debug: True to skip SSL verify for localhost tests.
    Returns: username and mqtt_token from arena-account.
    """
    global debug_toggle
    global _id_token
    global _mqtt_token
    debug_toggle = debug
    local_token = _local_token_check()
    if local_token:
        return local_token["username"]

    print("Using remote-authenticated MQTT token.")
    mqtt_json = _get_mqtt_token(host, realm, scene, username, _id_token)
    # save mqtt_token
    with open(_user_mqtt_path, mode="w") as d:
        d.write(mqtt_json)
    os.chmod(_user_mqtt_path, 0o600)  # set user-only perms.

    _mqtt_token = json.loads(mqtt_json)
    username = None
    if 'username' in _mqtt_token:
        username = _mqtt_token['username']
    print(f'ARENA Username: {username}')
    return _mqtt_token


def get_writable_scenes(host, debug=False):
    """ Request list of scene names for logged in user that user has publish permission for.
    host: The hostname of the ARENA webserver.
    debug: True to skip SSL verify for localhost tests.
    Returns: list of scenes.
    """
    global debug_toggle
    global _id_token
    debug_toggle = debug
    my_scenes = _get_my_scenes(host, _id_token)
    return json.loads(my_scenes)


def _local_token_check():
    # TODO: remove local check after ARTS supports mqtt_token passing
    # check for local mqtt_token first
    if os.path.exists(_local_mqtt_path):
        print("Using local MQTT token.")
        f = open(_local_mqtt_path, "r")
        mqtt_json = f.read()
        f.close()
        # TODO: check token expiration
        _mqtt_token = json.loads(mqtt_json)
        return _mqtt_token
    return None


def _get_csrftoken(host):
    # get the csrftoken for django
    global _csrftoken
    csrf_url = f'https://{host}/user/login'
    client = requests.session()
    verify = not debug_toggle
    client.get(csrf_url, verify=verify)  # sets cookie
    if 'csrftoken' in client.cookies:
        _csrftoken = client.cookies['csrftoken']
    elif 'csrf' in client.cookies:
        _csrftoken = client.cookies['csrf']
    else:
        _csrftoken = None
    return _csrftoken


def _get_gauthid(host):
    url = f'https://{host}/conf/gauth.json'
    return urlopen(url)


def _get_my_scenes(host, id_token):
    global _csrftoken
    url = f'https://{host}/user/my_scenes'
    if not _csrftoken:
        _csrftoken = _get_csrftoken(host)
    params = {"id_token": id_token}
    query_string = parse.urlencode(params)
    data = query_string.encode("ascii")
    return urlopen(url, data=data, csrf=_csrftoken)


def _get_user_state(host, id_token):
    global _csrftoken
    url = f'https://{host}/user/user_state'
    if not _csrftoken:
        _csrftoken = _get_csrftoken(host)
    params = {"id_token": id_token}
    query_string = parse.urlencode(params)
    data = query_string.encode("ascii")
    return urlopen(url, data=data, csrf=_csrftoken)


def _get_mqtt_token(host, realm, scene, username, id_token):
    global _csrftoken
    url = f'https://{host}/user/mqtt_auth'
    if not _csrftoken:
        _csrftoken = _get_csrftoken(host)
    params = {
        "id_auth": "google-installed",
        "username": username,
        "id_token": id_token,
        "realm": realm,
        "scene": scene
    }
    query_string = parse.urlencode(params)
    data = query_string.encode("ascii")
    return urlopen(url, data=data, csrf=_csrftoken)


def urlopen(url, data=None, creds=False, csrf=None):
    """ urlopen is for ARENA URL connections.
    url: the url to POST/GET.
    data: None for GET, add params for POST.
    creds: True to pass the MQTT token as a cookie.
    csrf: The csrftoken.
    """
    global debug_toggle
    global _mqtt_token
    try:
        req = request.Request(url)
        if creds:
            req.add_header("Cookie", f"mqtt_token={_mqtt_token['token']}")
        if csrf:
            req.add_header("Cookie", f"csrftoken={csrf}")
            req.add_header("X-CSRFToken", csrf)
        if debug_toggle:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            res = request.urlopen(req, data=data, context=context)
        else:
            res = request.urlopen(req, data=data)
        return res.read().decode('utf-8')
    except (requests.exceptions.ConnectionError, ConnectionError, URLError, HTTPError) as err:
        print("{0}: ".format(err)+url)
        if isinstance(err, HTTPError) and round(err.code, -2) == 400:
            # user not authorized on website yet, they don't have an ARENA username
            base_url = "{0.scheme}://{0.netloc}".format(urlsplit(url))
            print(f'Login with this this account on the website first:')
            print(f'Trying to open login page: {base_url}/user')
            try:
                webbrowser.open_new_tab(f'{base_url}/user')
            except (webbrowser.Error) as err:
                print("Console-only login. {0}".format(err))
        sys.exit("Terminating...")


def signout():
    if os.path.exists(_user_gauth_path):
        os.remove(_user_gauth_path)
    if os.path.exists(_user_mqtt_path):
        os.remove(_user_mqtt_path)
    print("Signed out of the ARENA.")


def _print_mqtt_token(jwt):
    print('ARENA MQTT Permissions')
    print('----------------------')
    print(f'User: {jwt["sub"]}')
    exp_str = time.strftime("%c", time.localtime(jwt["exp"]))
    print(f'Expires: {exp_str}')
    print('Publish topics:')
    for pub in jwt["publ"]:
        print(f'- {pub}')
    print('Subscribe topics:')
    for sub in jwt["subs"]:
        print(f'- {sub}')


def permissions():
    mqtt_path = None
    # check for local mqtt_token first
    if os.path.exists(_local_mqtt_path):
        print("Using local MQTT token.")
        mqtt_path = _local_mqtt_path
    elif os.path.exists(_user_mqtt_path):
        print("Using user MQTT token.")
        mqtt_path = _user_mqtt_path
    if mqtt_path:
        f = open(mqtt_path, "r")
        mqtt_json = f.read()
        f.close()
        mqtt_token = json.loads(mqtt_json)
        decoded = jwt.decode(mqtt_token["token"], options={
            "verify_signature": False})
        _print_mqtt_token(decoded)


if __name__ == '__main__':
    globals()[sys.argv[1]]()
