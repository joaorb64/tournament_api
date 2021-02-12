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

if os.path.exists("auth.json"):
	f = open('auth.json')
	auth_json = json.load(f)
	SMASHGG_KEYS = auth_json["SMASHGG_KEYS"]
else:
	SMASHGG_KEYS = os.environ.get("SMASHGG_KEYS")

smashgg_characters = json.loads(requests.get("https://api.smash.gg/characters").text)

def fetchPlayer(currKey, playerIndex):
	global leagues, tournaments, players, charname_to_braacket, cache, currentKey

	while playerIndex < len(players):
		fetchPlayerDo(currKey, playerIndex)
		playerIndex += len(SMASHGG_KEYS)

def fetchPlayerDo(currKey, playerIndex):
	global leagues, tournaments, players, charname_to_braacket, cache, currentKey, smashgg_characters, gameconfig

	print("Get smashgg data: "+str(playerIndex)+"/"+str(len(players)), end="\r")

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
						state
						country
					}
					images(type: "profile") {
						type
						url
					}
					player {
						gamerTag
						prefix
						sets(page: '''+str(i+1)+''', perPage: 25) {
							nodes {
								event {
									videogame {
										id
									}
								}
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
			# Skip set if no games
			if set_["games"] is None:
				continue
			# Skip set if not current videogame
			if set_.get("event", {}).get("videogame", {}).get("id", None) != gameconfig["smashgg_videogame_id"]:
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
										found = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == selection["selectionValue"]), None)
										if found:
											selections[selection["selectionValue"]] += 1
		
		mains = []

		if 1746 in selections.keys():
			del selections[1746] # Remove random
		
		most_common = selections.most_common(1)

		for character in selections.most_common(2):
			if(character[1] >= most_common[0][1]/3.0 or character[0] == most_common[0][0]):
				found = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == character[0]), None)
				if found:
					mains.append(charname_to_braacket.get(found["name"], found["name"]))
		
		resp["character_usage"] = {}
		for character in selections.most_common():
			found = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == character[0]), None)
			if found:
				resp["character_usage"][found["name"]] = selections[character[0]]
		
		del resp["player"]["sets"]
		
		if len(mains) > 0:
			resp["mains"] = mains

	cache[player["smashgg_id"]] = resp

	return

def get_smashgg_data(game):
	global leagues, tournaments, players, charname_to_braacket, cache, currentKey, gameconfig

	currentKey = 0
	cache = {}

	f = open('./games/'+game+'/config.json')
	gameconfig = json.load(f)

	f = open('./games/'+game+'/leagues.json')
	leagues = json.load(f)

	f = open('./out/'+game+'/alltournaments.json')
	tournaments = json.load(f)

	f = open('./out/'+game+'/allplayers.json')
	original_players = json.load(f)
	players = original_players["players"]

	threads = []

	f = open('./games/'+game+'/charnames_smashgg_to_braacket.json')
	charname_to_braacket = json.load(f)

	for i, k in enumerate(SMASHGG_KEYS):
		thread = Thread(target=fetchPlayer, args=[k, i])
		thread.daemon = True
		threads.append(thread)
		thread.start()

	for t in threads:
		t.join()

	with open('./out/'+game+'/smashgg_cache.json', 'w') as outfile:
		json.dump(cache, outfile, indent=4, sort_keys=True)

	with open('./out/'+game+'/allplayers.json', 'w') as outfile:
		json.dump(original_players, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		get_smashgg_data(game)
	else:
		for game in games:
			get_smashgg_data(game)
			time.sleep(1)