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
    if len(player_data.keys()) == 0:
      will_delete = True

  if will_delete == True:
    os.remove("./player_data/"+directory+"/data.json")
    os.rmdir("./player_data/"+directory)