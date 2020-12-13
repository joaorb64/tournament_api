import time
import datetime
import requests
import json
import pprint
import datetime
import os
from collections import Counter
import sys

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
	"Steve": "Steve"
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
smashgg_character_data = json.load(f)

for league in leagues:
	if len(sys.argv) >= 2:
		if league != sys.argv[1]:
			continue
	print(league)

	f = open('out/'+league+'/tournaments.json')
	tournaments = json.load(f)["tournaments"]

	f = open('out/'+league+'/players.json')
	original_players = json.load(f)
	players = original_players["players"]

	totalTournaments = len(tournaments.items())

	for i, tournament in enumerate(tournaments.items()):
		# not on smashgg, skip
		if not tournament[1]["link"]:
			print("Not on smashgg, skipping")
			continue
		
		tournament_slug_start = tournament[1]["link"].index("tournament/")
		slug = tournament[1]["link"][tournament_slug_start:]

		print(league + ": " + slug + " ["+str(i+1)+"/"+str(totalTournaments)+"]")

		# all players already got smashgg ids, skip
		allPlayersGotSmashggId = True

		if tournament[1]["ranking"] is None:
			continue

		for p in tournament[1]["ranking"]:
			if p not in players.keys():
				continue
			if "smashgg_id" not in players[p].keys():
				allPlayersGotSmashggId = False
				break
		if allPlayersGotSmashggId:
			print("All players already have smashgg data, skipping")
			continue

		page = 1

		while True:
			r = requests.post(
				'https://api.smash.gg/gql/alpha',
				headers={
					'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
				},
				json={
					'query': '''
					query evento($eventSlug: String!) {
						event(slug: $eventSlug) {
							entrants(query: {page: '''+str(page)+''', perPage: 80}) {
								nodes{
									name
									participants {
										user {
											id
											slug
											name
											authorizations {
												type
												externalUsername
											}
											player {
												gamerTag
												prefix
											}
											location {
												city
												country
											}
											images(type: "profile") {
												url
											}
										}
									}
								}
							}
						}
					},
				''',
					'variables': {
						"eventSlug": slug
					},
				}
			)
			time.sleep(1/len(SMASHGG_KEYS))
			currentKey = (currentKey+1)%len(SMASHGG_KEYS)

			resp = json.loads(r.text)

			if resp is None or \
			resp.get("data") is None or \
			resp["data"].get("event") is None or \
			resp["data"]["event"].get("entrants") is None:
				print(resp)
				break

			data_entrants = resp["data"]["event"]["entrants"]["nodes"]

			if data_entrants is None or len(data_entrants) == 0:
				break

			print("Page: "+str(page)+"\tEntries: "+str(len(data_entrants)))

			for gg_entrant in data_entrants:
				for braacket_entrant in tournament[1]["ranking"].items():
					if braacket_entrant[1]["tournament_name"] is None:
						continue
					if gg_entrant["name"] == braacket_entrant[1]["tournament_name"]:
						if gg_entrant["participants"][0]["user"] is None:
							# no smashgg data, nothing to do here
							continue

						player_obj = players.get(braacket_entrant[0])

						if player_obj == None or "smashgg_id" in player_obj.keys():
							# already did this
							continue

						player_obj["smashgg_id"] = gg_entrant["participants"][0]["user"]["id"]
						player_obj["smashgg_slug"] = gg_entrant["participants"][0]["user"]["slug"]
						player_obj["full_name"] = gg_entrant["participants"][0]["user"]["name"]
						player_obj["name"] = gg_entrant["participants"][0]["user"]["player"]["gamerTag"]
						player_obj["org"] = gg_entrant["participants"][0]["user"]["player"]["prefix"]

						if gg_entrant["participants"][0]["user"]["authorizations"] is not None:
							for authorization in gg_entrant["participants"][0]["user"]["authorizations"]:
								player_obj[authorization["type"].lower()] = authorization["externalUsername"]
						
						if gg_entrant["participants"][0]["user"]["location"] is not None:
							if gg_entrant["participants"][0]["user"]["location"]["city"] is not None:
								player_obj["city"] = gg_entrant["participants"][0]["user"]["location"]["city"]
							if gg_entrant["participants"][0]["user"]["location"]["country"] is not None:
								player_obj["country"] = gg_entrant["participants"][0]["user"]["location"]["country"]

						if gg_entrant["participants"][0]["user"]["images"] is not None:
							if len(gg_entrant["participants"][0]["user"]["images"]) > 0:
								player_obj["smashgg_image"] = gg_entrant["participants"][0]["user"]["images"][0]["url"]

						r = requests.post(
						'https://api.smash.gg/gql/alpha',
						headers={
							'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
						},
						json={
							'query': '''
							query user($userId: ID!) {
								user(id: $userId) {
									player {
										sets(page: 1, perPage: 30) {
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
									"userId": player_obj["smashgg_id"]
								},
							}
						)
						time.sleep(1/len(SMASHGG_KEYS))
						currentKey = (currentKey+1)%len(SMASHGG_KEYS)

						resp = json.loads(r.text)
						
						if resp is not None and \
						"data" in resp.keys() and \
						resp["data"]["user"]["player"]["sets"] is not None and \
						resp["data"]["user"]["player"]["sets"]["nodes"] is not None:
							selections = Counter()

							for set_ in resp["data"]["user"]["player"]["sets"]["nodes"]:
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
													if player_obj["smashgg_id"] == participant_id:
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
							
							player_obj["character_usage"] = {}
							for character in selections.most_common():
								found = next((c for c in smashgg_character_data["character"] if c["id"] == character[0]), None)
								if found:
									player_obj["character_usage"][found["name"]] = selections[character[0]]
							
							if len(mains) > 0:
								player_obj["mains"] = mains
						break

			page += 1
	
	with open('out/'+league+'/players.json', 'w') as outfile:
		json.dump(original_players, outfile, indent=4, sort_keys=True)