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

# values = [
#     ['a1', 'b1', 'c1', 123],
#     ['a2', 'b2', 'c2', 456]
# ]

# data = {'values': values}

gsheet = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='PlayerData'
).execute()

all_players = {
    "players": [],
    "mapping": {}
}

# Load from spreadsheet

for player in gsheet["values"][1:]:
    # 'Nick', 'Org', 'Estado', 'Braacket Links', 'Nome real', 'Twitter', 'Mains'
    while len(player) < 7:
        player.append("")

    link = player[3].split("\n")[0]

    all_players["players"].append({
        "name": player[0],
        "org": player[1],
        "state": player[2],
        "braacket_links": player[3].split("\n"),
        "full_name": player[4],
        "twitter": player[5],
        "mains": player[6].split("\n"),
        "skins": [0 for m in player[6].split("\n")]
    })

    player_obj = all_players["players"][-1]

    for i, main in enumerate(player_obj["mains"]):
        if len(main) == 0:
            continue
        if main[-1].isnumeric():
            player_obj["skins"][i] = int(main[-1])
            player_obj["mains"][i] = player_obj["mains"][:-1]

    for link in player[3].split("\n"):
        all_players["mapping"][link] = len(all_players["players"]) - 1

with open('allplayers.json', 'w') as outfile:
    json.dump(all_players, outfile, indent=4, sort_keys=True)


'''
# Upload inicial

directories = os.listdir("./player_data")

with open('allplayers.csv', mode='w') as player_csv:

    player_csv_writer = csv.writer(player_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for directory in directories:
        with open('player_data/'+directory+'/data.json', 'r') as player_file:

            player_data = json.load(player_file)

            if len(player_data.keys()) == 0:
                continue

            braacket_links = None

            if player_data.get("braacket_link"):
                braacket_links = player_data.get("braacket_link").values()
                braacket_links = '\n'.join([re.split('/|\?',link)[-2] for link in braacket_links])
                
            player_csv_writer.writerow([
                player_data.get("name"),
                player_data.get("state"),
                braacket_links,
                "",
                player_data.get("full_name"),
                player_data.get("twitter"),
                "\n".join([main.get("name") for main in player_data.get("mains")]) if player_data.get("mains") is not None else ""
            ])
'''
'''
r = requests.get('https://docs.google.com/spreadsheets/d/1ppEf-oCuoQ9i_EJsZao4Lb8QXnRi0xkGj7JxJmIPYvI/export?format=csv&gid=0')
data = StringIO(r.text)

csv_reader = csv.DictReader(data)

line_count = 0

print(csv_reader)

for row in csv_reader:
    print(row)
'''
'''
# atualizar dados de jogadores sem ter que recriar tudo~

def update(d, u):
	for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
					d[k] = update(d.get(k, {}), v)
			else:
					d[k] = v
	return d

with open('allplayers.json', 'r') as allplayers_data:
    allplayers = json.load(allplayers_data)

directories = os.listdir("./player_data")

with open('allplayers.csv', mode='w') as player_csv:

    player_csv_writer = csv.writer(player_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for i, player in enumerate(allplayers["players"]):
        print("["+str(i)+"/"+str(len(allplayers["players"])))
        done = False
        for directory in directories:
            if done:
                break
            with open('player_data/'+directory+'/data.json', 'r') as player_file:

                player_data = json.load(player_file)

                if len(player_data.keys()) == 0:
                    continue

                if "braacket_link" not in player_data.keys():
                    continue

                mapping = {}

                if player_data.get("braacket_link"):
                    for link in player_data.get("braacket_link"):
                        if link == "prbth":
                            mapping[re.split('/|\?',player_data["braacket_link"][link])[-1]] = link
                        else:
                            mapping[re.split('/|\?',player_data["braacket_link"][link])[-2]] = link

                for i, link in enumerate(player["braacket_links"]):
                    if link in mapping.keys():
                        player["braacket_links"][i] = mapping[link]+":"+link
        
        player_csv_writer.writerow([
            player.get("name"),
            player.get("org"),
            player.get("state"),
            '\n'.join(player.get("braacket_links")),
            player.get("full_name"),
            player.get("twitter"),
            '\n'.join(player.get("mains")),
        ])
    
'''