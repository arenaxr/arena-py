"""
arena/auth.py - Authentication methods for accessing the ARENA.
"""

import json
import os.path
import pickle
import ssl
import webbrowser
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession

debug_toggle = False


def authenticate(realm, scene, broker, webhost, debug=False):
    global debug_toggle
    debug_toggle = debug
    # begin authentication flow
    scopes = ["openid",
              "https://www.googleapis.com/auth/userinfo.profile",
              "https://www.googleapis.com/auth/userinfo.email"]
    cpath = f'{str(Path.home())}/.arena_google_auth'
    mtpath = f'{str(Path.home())}/.arena_mqtt_auth'
    creds = None
    browser = None
    try:
        browser = webbrowser.get()
    except (webbrowser.Error) as err:
        print("Console-only login. {0}".format(err))

    # store the user's access and refresh tokens
    if os.path.exists(cpath):
        with open(cpath, 'rb') as token:
            creds = pickle.load(token)
        session = AuthorizedSession(creds)
    # if no credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            gauth_json = get_gauthid(webhost)
            flow = InstalledAppFlow.from_client_config(
                json.loads(gauth_json), scopes)
            if browser:
                # TODO: select best client port to avoid likely conflicts
                creds = flow.run_local_server(port=8989)
            else:
                creds = flow.run_console()
        session = flow.authorized_session()
        with open(cpath, 'wb') as token:
            # save the credentials for the next run
            pickle.dump(creds, token)
        os.chmod(cpath, 0o600)  # set user-only perms.

    id_token = creds.id_token

    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    print(profile_info)

    # use JWT for authentication
    if profile_info != None:
        mqtt_json = None
        user = profile_info['email']
        if os.path.exists(mtpath):
            f = open(mtpath, "r")
            mqtt_json = f.read()
            f.close()
            # TODO: check old token for exp.
        # if no credentials available, get them.
        if not mqtt_json:
            mqtt_json = get_mqtt_token(broker, realm, scene, user, id_token)
            # save mqtt_token
            with open(mtpath, mode="w") as d:
                d.write(mqtt_json)
            os.chmod(mtpath, 0o600)  # set user-only perms.

        tokeninfo = json.loads(mqtt_json)
        print('tokeninfo: '+json.dumps(tokeninfo))
        if 'token' in tokeninfo:
            token = tokeninfo['token']
    # end authentication flow
    return user, token


# TODO: will be deprecated after using arena-account
def get_gauthid(webhost):
    url = f'https://{webhost}/conf/gauth.json'
    return _urlopen(url)


def get_mqtt_token(broker, realm, scene, user, id_token):
    url = f'https://{broker}/auth/'
    params = {
        "id_auth": "google",
        "username": user,
        "id_token": id_token,
        "realm": realm,
        "scene": scene
    }
    query_string = parse.urlencode(params)
    data = query_string.encode("ascii")
    return _urlopen(url, data)


def _urlopen(url, data=None):
    global debug_toggle
    try:
        if debug_toggle:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            res = request.urlopen(url, data=data, context=context)
        else:
            res = request.urlopen(url, data=data)
        return res.read().decode('utf-8')
    except (URLError, HTTPError) as err:
        print("Error: {0}".format(err))
        return {}
