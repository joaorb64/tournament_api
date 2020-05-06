import braacket
import pprint
import json
import os
import unicodedata
import re
import copy

directories = os.listdir("./player_data")

for directory in directories:
  will_delete = False

  with open('player_data/'+directory+'/data.json', 'r') as player_file:

    player_data = json.load(player_file)

    if len(player_data.keys()) == 0 or "rank" not in player_data.keys():
      will_delete = True
    elif "rank" in player_data.keys():
      player_data["rank"] = {}
      with open('player_data/'+directory+'/data.json', 'w') as outfile:
        json.dump(player_data, outfile, indent=4, sort_keys=True)

  if will_delete == True:
    os.remove("./player_data/"+directory+"/data.json")
    os.rmdir("./player_data/"+directory)