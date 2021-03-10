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
	global leagues, tournaments, players, charname_to_braacket, cache, previous_cache, currentKey, smashgg_characters, gameconfig

	print("Get smashgg data: "+str(playerIndex)+"/"+str(len(players)), end="\r")

	if playerIndex >= len(players):
		return

	player = players[playerIndex]

	if "smashgg_id" not in player.keys():
		return
	
	# Get profile data and latest set
	profileRequest = requests.post('https://api.smash.gg/gql/alpha',
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
						sets(page: 1, perPage: 1) {
							nodes {
								id
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
	)
	time.sleep(1)
	
	try:
		profileData = json.loads(profileRequest.text)
	except Exception as e:
		print(profileRequest.text)
		print(e)
		return

	if len(profileData) == 0 or "data" not in profileData.keys() or "user" not in profileData["data"]:
		print("Erro ao obter")
		print(profileData)
		return
	
	resp = profileData["data"]["user"]

	# Check if no new sets
	newSets = True


	'''if previous_cache.get(str(player["smashgg_id"]), None) is not None and "latestSetId" in previous_cache[str(player["smashgg_id"])]:
		if resp.get("player", {}).get("sets", None) is not None:
			if len(resp["player"]["sets"]["nodes"]) > 0 and resp["player"]["sets"]["nodes"][0] is not None:
				if resp["player"]["sets"]["nodes"][0]["id"] == previous_cache[str(player["smashgg_id"])]["latestSetId"]:
					newSets = False
					if "character_usage" in previous_cache[str(player["smashgg_id"])]:
						resp["character_usage"] = previous_cache[str(player["smashgg_id"])]["character_usage"]
					if "mains" in previous_cache[str(player["smashgg_id"])]:
						resp["mains"] = previous_cache[str(player["smashgg_id"])]["mains"]'''

	if newSets:
		r = []

		for i in range(5):
			resposta = requests.post(
			'https://api.smash.gg/gql/alpha',
			headers={
				'Authorization': 'Bearer'+currKey,
			},
			json={
				'query': '''
				query user($userId: ID!) {
					user(id: $userId) {
						player {
							sets(page: '''+str(i+1)+''', perPage: 10) {
								nodes {
									id
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
			)
			time.sleep(1)

			if resposta != None:
				try:
					r.append(json.loads(resposta.text))

					gotSets = r[-1].get("data", {}).get("user", {}).get("player", {}).get("sets", {}).get("nodes", [])

					if gotSets is None or len(gotSets) == 0:
						break
				except Exception as e:
					print(e)
					break

		if "sets" not in resp["player"]:
			resp["player"]["sets"] = {}

		resp["player"]["sets"]["nodes"] = []

		for setGroup in r:
			if setGroup.get("data", {}).get("user", {}).get("player", {}).get("sets", {}).get("nodes", {}):
				resp["player"]["sets"]["nodes"] += \
					setGroup["data"]["user"]["player"]["sets"]["nodes"]
		
		# character usage, mains
		if resp["player"]["sets"] is not None and \
		resp["player"]["sets"]["nodes"] is not None:
			selections = Counter()

			for set_ in resp["player"]["sets"]["nodes"]:
				if set_ is None:
					continue
				# Skip set if no games
				if set_["games"] is None:
					continue
				# Skip set if not current videogame
				if set_.get("event", None) == None:
					continue
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

			selectionsWithoutRandom = selections.copy()

			for selection in list(selectionsWithoutRandom):
				selectionName = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == selection), None)
				if selectionName and "random" in selectionName["name"].lower():
					del selectionsWithoutRandom[selection]

			most_common = selectionsWithoutRandom.most_common(1)

			for character in selectionsWithoutRandom.most_common(2):
				if(character[1] >= most_common[0][1]/3.0 or character[0] == most_common[0][0]):
					found = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == character[0]), None)
					if found:
						mains.append(charname_to_braacket.get(found["name"], found["name"]))
			
			resp["character_usage"] = {}

			for character in selections.most_common():
				found = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == character[0]), None)
				if found:
					resp["character_usage"][charname_to_braacket.get(found["name"], found["name"])] = selections[character[0]]

			try:
				resp["latestSetId"] = resp["player"]["sets"]["nodes"][0]["id"]
			except Exception as e:
				print(e)

			del resp["player"]["sets"]
			
			if len(mains) > 0:
				resp["mains"] = mains
	
	if "sets" in resp["player"]:
		del resp["player"]["sets"]

	cache[player["smashgg_id"]] = resp

	return

def get_smashgg_data(game):
	global leagues, tournaments, players, charname_to_braacket, cache, currentKey, gameconfig, previous_cache

	currentKey = 0
	cache = {}

	f = open('./games/'+game+'/config.json')
	gameconfig = json.load(f)

	f = open('./games/'+game+'/leagues.json')
	leagues = json.load(f)

	f = open('./out/'+game+'/alltournaments.json')
	tournaments = json.load(f)

	previous_cache = {}
	try:
		f = open('./out/'+game+'/smashgg_cache.json')
		previous_cache = json.load(f)
	except:
		pass

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
	
	for c in cache:
		previous_cache[str(c)] = cache[c]

	with open('./out/'+game+'/smashgg_cache.json', 'w') as outfile:
		json.dump(previous_cache, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		get_smashgg_data(game)
	else:
		for game in games:
			get_smashgg_data(game)
			time.sleep(1)