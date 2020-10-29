import json
import os
import unicodedata

def update(d, u):
	for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
					d[k] = update(d.get(k, {}), v)
			else:
					d[k] = v
	return d

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

        player = update(player, player2)

        allplayers["players"][j] = None

# Remove Null entries
moveup = 0
for i, player in enumerate(allplayers["players"]):
  if player is None:
    moveup += 1
    continue
  for link in player["braacket_links"]:
    allplayers["mapping"][link] -= moveup

allplayers["players"] = [i for i in allplayers["players"] if i] 

with open('allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)