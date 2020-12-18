import time
import datetime
import requests
import json
import pprint
import datetime
import os
from collections import Counter
import sys
from threading import Thread

def update(d, u):
	for k, v in u.items():
		if isinstance(v, collections.abc.Mapping):
			d[k] = update(d.get(k, {}), v)
		else:
			d[k] = v
	return d

characters = {
	"Mario": "Mario",
	"Donkey Kong": "Donkey Kong",
	"Link": "Link",
	"Samus": "Samus",
	"Dark Samus": "Dark Samus",
	"Yoshi": "Yoshi",
	"Kirby": "Kirby",
	"Fox": "Fox",
	"Pikachu": "Pikachu",
	"Luigi": "Luigi",
	"Ness": "Ness",
	"Captain Falcon": "Captain Falcon",
	"Jigglypuff": "Jigglypuff",
	"Peach": "Peach",
	"Daisy": "Daisy",
	"Bowser": "Bowser",
	"Ice Climbers": "Ice Climbers",
	"Sheik": "Sheik",
	"Zelda": "Zelda",
	"Dr. Mario": "Dr Mario",
	"Pichu": "Pichu",
	"Falco": "Falco",
	"Marth": "Marth",
	"Lucina": "Lucina",
	"Young Link": "Young Link",
	"Ganondorf": "Ganondorf",
	"Mewtwo": "Mewtwo",
	"Roy": "Roy",
	"Chrom": "Chrom",
	"Mr. Game & Watch": "Mr Game And Watch",
	"Meta Knight": "Meta Knight",
	"Pit": "Pit",
	"Dark Pit": "Dark Pit",
	"Zero Suit Samus": "Zero Suit Samus",
	"Wario": "Wario",
	"Snake": "Snake",
	"Ike": "Ike",
	"Pokemon Trainer": "Pokemon Trainer",
	"Diddy Kong": "Diddy Kong",
	"Lucas": "Lucas",
	"Sonic": "Sonic",
	"King Dedede": "King Dedede",
	"Olimar": "Olimar",
	"Lucario": "Lucario",
	"R.O.B.": "Rob",
	"Toon Link": "Toon Link",
	"Wolf": "Wolf",
	"Villager": "Villager",
	"Mega Man": "Mega Man",
	"Wii Fit Trainer": "Wii Fit Trainer",
	"Rosalina": "Rosalina And Luma",
	"Little Mac": "Little Mac",
	"Greninja": "Greninja",
	"Mii Brawler": "Mii Brawler",
	"Mii Swordfighter": "Mii Swordfighter",
	"Mii Gunner": "Mii Gunner",
	"Palutena": "Palutena",
	"Pac-Man": "Pac Man",
	"Robin": "Robin",
	"Shulk": "Shulk",
	"Bowser Jr.": "Bowser Jr",
	"Duck Hunt": "Duck Hunt",
	"Ryu": "Ryu",
	"Ken": "Ken",
	"Cloud": "Cloud",
	"Corrin": "Corrin",
	"Bayonetta": "Bayonetta",
	"Inkling": "Inkling",
	"Ridley": "Ridley",
	"Simon Belmont": "Simon",
	"Richter": "Richter",
	"King K. Rool": "King K Rool",
	"Isabelle": "Isabelle",
	"Incineroar": "Incineroar",
	"Piranha Plant": "Piranha Plant",
	"Joker": "Joker",
	"Hero": "Hero",
	"Banjo-Kazooie": "Banjo-Kazooie",
	"Terry": "Terry",
	"Byleth": "Byleth",
	"Min Min": "Min Min",
	"Steve": "Steve",
	"Sephiroth": "Sephiroth"
}

if os.path.exists("auth.json"):
  f = open('auth.json')
  auth_json = json.load(f)
  SMASHGG_KEYS = auth_json["SMASHGG_KEYS"]
else:
  SMASHGG_KEYS = os.environ.get("SMASHGG_KEYS")

currentKey = 0

f = open('leagues.json')
leagues = json.load(f)

f = open('ultimate.json')
smashgg_character_data = json.load(f)["entities"]

f = open('out/smashgg_cache.json')
smashgg_cache = json.load(f)

f = open('out/allplayers.json')
original_players = json.load(f)
players = original_players["players"]

for i, player in enumerate(players):
	print("Append cache: "+str(i)+"/"+str(len(players)), end="\r")

	if "smashgg_id" not in player.keys():
		continue

	if str(player["smashgg_id"]) in smashgg_cache.keys():
		resp = smashgg_cache[str(player["smashgg_id"])]
	
		player["smashgg_id"] = resp["id"]
		player["smashgg_slug"] = resp["slug"]
		player["full_name"] = resp["name"]
		player["name"] = resp["player"]["gamerTag"]
		player["org"] = resp["player"]["prefix"]

		if resp["authorizations"] is not None:
			for authorization in resp["authorizations"]:
				player[authorization["type"].lower()] = authorization["externalUsername"]
		
		if resp["location"] is not None:
			if resp["location"]["city"] is not None:
				player["city"] = resp["location"]["city"]
			if resp["location"]["country"] is not None:
				player["country"] = resp["location"]["country"]

		if resp["images"] is not None:
			if len(resp["images"]) > 0:
				player["smashgg_image"] = resp["images"][0]["url"]

		# character usage, mains
		if resp["player"]["sets"] is not None and \
		resp["player"]["sets"]["nodes"] is not None:
			selections = Counter()

			for set_ in resp["player"]["sets"]["nodes"]:
				if set_["games"] is None:
					continue
				for game in set_["games"]:
					if game["selections"] is None:
						continue
					for selection in game["selections"]:
						if selection.get("entrant"):
							if selection.get("entrant").get("participants"):
								if len(selection.get("entrant").get("participants")) > 0:
									if selection.get("entrant").get("participants") is None:
										continue
									if selection.get("entrant").get("participants")[0] is None:
										continue
									if selection.get("entrant").get("participants")[0]["user"] is None:
										continue
									participant_id = selection.get("entrant").get("participants")[0]["user"]["id"]
									if player["smashgg_id"] == participant_id:
										if selection["selectionValue"] is not None:
											selections[selection["selectionValue"]] += 1
			
			mains = []

			if 1746 in selections.keys():
				del selections[1746] # Remove random
			
			most_common = selections.most_common(1)

			for character in selections.most_common(2):
				if(character[1] > most_common[0][1]/3.0):
					found = next((c for c in smashgg_character_data["character"] if c["id"] == character[0]), None)
					if found:
						mains.append(characters[found["name"]])
			
			player["character_usage"] = {}
			for character in selections.most_common():
				found = next((c for c in smashgg_character_data["character"] if c["id"] == character[0]), None)
				if found:
					player["character_usage"][found["name"]] = selections[character[0]]
			
			if len(mains) > 0:
				player["mains"] = mains

print("")

with open('out/allplayers.json', 'w') as outfile:
	json.dump(original_players, outfile, indent=4, sort_keys=True)