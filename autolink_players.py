import json
import os
import unicodedata

f = open('allplayers.json')
allplayers = json.load(f)

for i, player in enumerate(allplayers["players"]):
  for j, player2 in enumerate(allplayers["players"]):
    if player is None or player2 is None:
      continue
    if player is player2:
      continue

    if "smashgg_id" in player.keys() and "smashgg_id" in player2.keys():
      if player["smashgg_id"] == player2["smashgg_id"]:
        print(player["name"] + " is " + player2["name"])
        for link in player2["braacket_links"]:
          if link not in player2["braacket_links"]:
            player["braacket_links"].append(link)
            allplayers["mapping"][link] = i
        allplayers["players"][j] = None


with open('allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)