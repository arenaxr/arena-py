"""
*TL;DR Wrapper to access google sheets and google drive

You need the following:
1. A Google Cloud Platform project with the *Google Sheets API* and *Google Drive API* enabled: https://developers.google.com/workspace/guides/create-project
2. Authorization credentials for a desktop application (pasted into 'credentials.json'): https://developers.google.com/workspace/guides/create-credentials

Details: https://developers.google.com/apps-script/api/quickstart/python?hl=en
"""
from __future__ import print_function
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import json
import uuid

class GoogleClientWrapper:
    """Wrapper to access google sheets and google drive
       Based on: https://developers.google.com/sheets/api/quickstart/python, https://developers.google.com/drive/api/v3/quickstart/python
    """
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive']
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', GoogleClientWrapper.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GoogleClientWrapper.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.gs_service = build('sheets', 'v4', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)

    def gs_aslist(self, sheet_id, table_range_name):
        """
            Opens a Google Sheet and converts a table within a given range into a list
            of dictionaries using the first line (table header) as keys.

            Example:

              col 1    col 2    col 3
              1       2       3
              4       5       6

              Returns:
              [
                {'col_1': '1', 'col_2': '2', 'col_3': '3'},
                {'col_1': '4', 'col_2': '5', 'col_3': '6'},
              ]

            Note that spaces in key names are replaced by '_'.

            Parameters
            ----------
            sheet_id: str
              The google spreadsheet id
            table_range_name: str
              The A1 or R1C1 range of the data table. e.g: Sheet1!A1:F10

           See: https://developers.google.com/sheets/api/guides/concepts
        """

        # Call the Sheets API
        sheet = self.gs_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id,
                range=table_range_name).execute()
        values = result.get('values', [])
        if len(values) == 0: return []
        # Convert spreadsheet table into list of dict()
        columns = list(map(lambda v: v.replace(' ', '_'), values[0]))
        res_list = []
        for v in values[1:]:
            res_list.append(dict(map(lambda k, v: (k, v), columns, v)))
        return res_list

    def gd_save_json(self, file_id, obj_to_save, gd_fn=None, formatted_json=True):
        """
            Save disctionary into a .json file stored in google drive
            The destination file must exist (e.g. create an empty .json file)
            It will update the google drive filename to the given filename

            Parameters
            ----------
            file_id: str
                The google drive file id
            obj_to_save: object
                Json-serializable object to save to the json file
            fn: str
                Set the google file to given filename
            formatted_json: boolean
                Save formatted json
        """
        if formatted_json:
            json_str = json.dumps(obj_to_save, indent=4, sort_keys=True)
        else: json_str = json.dumps(obj_to_save)

        fn = f'{uuid.uuid4()}.json'
        fp = open(fn,"w")
        fp.write(json_str)
        fp.close()

        if gd_fn:
            file_metadata = {
                "name": gd_fn,
            }
        else: file_metadata = None

        media = MediaFileUpload(fn, resumable=True)
        file = self.drive_service.files().update(fileId=file_id, body=file_metadata, media_body=media).execute()

        os.remove(fn)
