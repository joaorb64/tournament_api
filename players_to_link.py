from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import requests
import csv
from io import StringIO
import pprint
import json
import os
import unicodedata
import re
import copy

import httplib2
from apiclient import discovery
from google.oauth2 import service_account


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

secret_file = os.path.join(os.getcwd(), 'credentials.json')

credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=SCOPES)
service = discovery.build('sheets', 'v4', credentials=credentials)

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1ppEf-oCuoQ9i_EJsZao4Lb8QXnRi0xkGj7JxJmIPYvI'

with open('allplayers.json', 'r') as outfile:
  values = []
  
  allplayers = json.load(outfile)

  playernames = [p["name"] for p in allplayers["players"]]

  for player in playernames:
    playernames_copy = list(playernames)
    playernames_copy.remove(player)

    ratios = process.extract(player, playernames_copy, limit=3)

    values.append([
      player,
      ratios[0][0], ratios[0][1],
      ratios[1][0], ratios[1][1],
      ratios[2][0], ratios[2][1]
    ])
  
  service.spreadsheets().values().clear(
      spreadsheetId=SPREADSHEET_ID,
      range='PlayersToLink!A2:G',
      body={}
  ).execute()

  service.spreadsheets().values().update(
      spreadsheetId=SPREADSHEET_ID,
      range='PlayersToLink!A2',
      body={"values": values},
      valueInputOption='USER_ENTERED'
  ).execute()