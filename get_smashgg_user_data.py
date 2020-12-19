import time
import datetime
import requests
import json
import pprint
import datetime
import os
from collections import Counter
import sys
from threading import Thread, Lock

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

f = open('out/alltournaments.json')
tournaments = json.load(f)

f = open('out/allplayers.json')
original_players = json.load(f)
players = original_players["players"]

cache = {}

def fetchPlayer(currKey, playerIndex):
	while playerIndex < len(players):
		fetchPlayerDo(currKey, playerIndex)
		playerIndex += len(SMASHGG_KEYS)

def fetchPlayerDo(currKey, playerIndex):
	print(str(playerIndex)+"/"+str(len(players)))

	if playerIndex >= len(players):
		return

	player = players[playerIndex]

	if "smashgg_id" not in player.keys():
		return
	
	r = []

	for i in range(2):
		r.append(requests.post(
		'https://api.smash.gg/gql/alpha',
		headers={
			'Authorization': 'Bearer'+currKey,
		},
		json={
			'query': '''
			query user($userId: ID!) {
				user(id: $userId) {
					id
					slug
					name
					authorizations {
						type
						externalUsername
					}
					location {
						city
						country
					}
					images(type: "profile") {
						url
					}
					player {
						gamerTag
						prefix
						sets(page: '''+str(i+1)+''', perPage: 25) {
							nodes {
								games {
									selections {
										entrant {
											participants {
												user {
													id
												}
											}
										}
										selectionValue
									}
								}
							}
						}
					}
				}
			}
			''',
				'variables': {
					"userId": str(player["smashgg_id"])
				},
			}
		))
		time.sleep(1)

	resp = json.loads(r[0].text)
	resp2 = json.loads(r[1].text)

	if resp.get("data", {}).get("user", {}).get("player", {}).get("sets", {}).get("nodes", {}) and \
	resp2.get("data", {}).get("user", {}).get("player", {}).get("sets", {}).get("nodes", {}):
		resp["data"]["user"]["player"]["sets"]["nodes"] = \
			resp["data"]["user"]["player"]["sets"]["nodes"] + resp2["data"]["user"]["player"]["sets"]["nodes"]

	if resp is None or "data" not in resp.keys():
		print("Erro ao obter")
		print(resp)
		return
	
	resp = resp["data"]["user"]
	
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
										# only get selections for smash!
										found = next((c for c in smashgg_character_data["character"] if c["id"] == selection["selectionValue"]), None)
										if found:
											selections[selection["selectionValue"]] += 1
		
		mains = []

		if 1746 in selections.keys():
			del selections[1746] # Remove random
		
		most_common = selections.most_common(1)

		for character in selections.most_common(2):
			if(character[1] >= most_common[0][1]/3.0 or character[0] == most_common[0][0]):
				found = next((c for c in smashgg_character_data["character"] if c["id"] == character[0]), None)
				if found:
					mains.append(characters[found["name"]])
		
		resp["character_usage"] = {}
		for character in selections.most_common():
			found = next((c for c in smashgg_character_data["character"] if c["id"] == character[0]), None)
			if found:
				resp["character_usage"][found["name"]] = selections[character[0]]
		
		del resp["player"]["sets"]
		
		if len(mains) > 0:
			resp["mains"] = mains

	cache[player["smashgg_id"]] = resp

	return

threads = []
cache_lock = Lock()

for i, k in enumerate(SMASHGG_KEYS):
	thread = Thread(target=fetchPlayer, args=[k, i])
	thread.daemon = True
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()

with open('out/smashgg_cache.json', 'w') as outfile:
	json.dump(cache, outfile, indent=4, sort_keys=True)

with open('out/allplayers.json', 'w') as outfile:
	json.dump(original_players, outfile, indent=4, sort_keys=True)