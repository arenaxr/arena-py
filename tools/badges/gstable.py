"""
*TL;DR
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

You need the following:
1. A Google Cloud Platform project with the *Google Sheets API* enabled: https://developers.google.com/workspace/guides/create-project
2. Authorization credentials for a desktop application (pasted into 'credentials.json'): https://developers.google.com/workspace/guides/create-credentials

Details: https://developers.google.com/apps-script/api/quickstart/python?hl=en
"""
from __future__ import print_function

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleSheetTable:
    """Access google sheet and get data
       Based on: https://developers.google.com/sheets/api/quickstart/python
    """
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file(
                'token.json', GoogleSheetTable.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GoogleSheetTable.SCOPES)
                if "SSH_TTY" in os.environ or "SSH_CLIENT" in os.environ:
                    creds = flow.run_console()
                else:
                    creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()

    def aslist(self, sheet_id, table_range_name):
        """Return list of dict() with table contents
           args:
           sheet_id
             the google spreadsheet id
           table_range_name
             the A1 or R1C1 range of the data table. e.g: Sheet1!A1:F10

           See: https://developers.google.com/sheets/api/guides/concepts
        """

        # Call the Sheets API
        result = self.sheet.values().get(spreadsheetId=sheet_id,
                                         range=table_range_name).execute()
        values = result.get('values', [])
        if len(values) == 0:
            return []
        # Convert spreadsheet table into list of dict()
        columns = list(map(lambda v: v.replace(' ', '_'), values[0]))
        res_list = []
        for v in values[1:]:
            res_list.append(dict(map(lambda k, v: (k, v), columns, v)))
        return res_list

    def addrow(self, sheet_id, table_range_name, row):
        """Add a row as list and return list of dict() with table contents
        args:
        sheet_id
            the google spreadsheet id
        table_range_name
            the A1 or R1C1 range of the data table. e.g: Sheet1!A1:F10
        row
            the list to add at the end

        See: https://developers.google.com/sheets/api/guides/concepts
        """

        values = [[]]
        for cell in row:
            values[0].append(cell)
        body = {'values': values}
        # Add new row from  Sheets API
        result = self.sheet.values().append(spreadsheetId=sheet_id,
                                            range=table_range_name,
                                            valueInputOption='RAW',
                                            insertDataOption='INSERT_ROWS',
                                            body=body).execute()

        # Get updated rows from  Sheets API
        result = self.sheet.values().get(spreadsheetId=sheet_id,
                                         range=table_range_name).execute()
        values = result.get('values', [])
        if len(values) == 0:
            return []
        # Convert spreadsheet table into list of dict()
        columns = list(map(lambda v: v.replace(' ', '_'), values[0]))
        res_list = []
        for v in values[1:]:
            res_list.append(dict(map(lambda k, v: (k, v), columns, v)))
        return res_list

    def updaterow(self, sheet_id, table_range_name, row):
        """Add a row as list and return list of dict() with table contents
        args:
        sheet_id
            the google spreadsheet id
        table_range_name
            the A1 or R1C1 range of the data table. e.g: Sheet1!A1:F10
        row
            the list to overwrite at the table_range_name cell

        See: https://developers.google.com/sheets/api/guides/concepts
        """

        values = [[]]
        for cell in row:
            values[0].append(cell)
        body = {'values': values}
        # Add new row from  Sheets API
        print(f"Updating {table_range_name}")
        result = self.sheet.values().update(spreadsheetId=sheet_id,
                                            range=table_range_name,
                                            valueInputOption='RAW',
                                            body=body).execute()

        # Get updated rows from  Sheets API
        result = self.sheet.values().get(spreadsheetId=sheet_id,
                                         range=table_range_name).execute()
        values = result.get('values', [])
        if len(values) == 0:
            return []
        # Convert spreadsheet table into list of dict()
        columns = list(map(lambda v: v.replace(' ', '_'), values[0]))
        res_list = []
        for v in values[1:]:
            res_list.append(dict(map(lambda k, v: (k, v), columns, v)))
        return res_list
