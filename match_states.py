import json
import os
import unicodedata
import sys
from threading import Thread

def remove_accents_lower(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

f = open('countries+states+cities.json')
countries = json.load(f)

cityToState = {}

for country in countries:
	for state in country["states"]:
		for c in state["cities"]:
			if country["iso2"] not in cityToState:
				cityToState[country["iso2"]] = {}
			city_name = remove_accents_lower(c["name"])
			if city_name not in cityToState[country["iso2"]]:
				cityToState[country["iso2"]][city_name] = state["state_code"]

def match_player_state(i, skipsize):
	global players

	while i < len(players["players"]):
		match_player_state_do(i)
		i+=skipsize

def match_player_state_do(i):
	global players

	if i >= len(players["players"]):
		return

	player = players["players"][i]

	print("Match states: "+str(i)+"/"+str(len(players["players"])-1))

	if "country" in player.keys() and player["country"] is not None:
		country = next(
			(c for c in countries if remove_accents_lower(c["name"]) == remove_accents_lower(player["country"])),
			None
		)

		if country is not None:
			player["country_code"] = country["iso2"]

			if "state" in player.keys():
				return

			if "city" in player.keys() and player["city"] is not None:
				# State explicit?
				split = player["city"].split(" ")

				for part in split[::-1]:
					# Find by state code
					state = next(
						(st for st in country["states"] if remove_accents_lower(st["state_code"]) == remove_accents_lower(part)),
						None
					)

					# Find by state name
					if state == None:
						state = next(
							(st for st in country["states"] if remove_accents_lower(st["name"]) == remove_accents_lower(part)),
							None
						)

					if state is not None:
						player["state"] = state["state_code"]
						break

				if "state" not in player.keys() or player["state"] is None:
					# no, so get by City
					state = cityToState.get(player["country_code"], {}).get(remove_accents_lower(player["city"]), None)

					if state is not None:
						player["state"] = state
	return

def match_states(game):
	global players

	print("Game: "+game)

	f = open('./out/'+game+'/allplayers.json')
	players = json.load(f)

	threads = []
	thread_number = 8

	for i in range(thread_number):
		thread = Thread(target=match_player_state, args=[i, thread_number])
		thread.daemon = True
		threads.append(thread)
		thread.start()

	for t in threads:
		t.join()

	with open('./out/'+game+'/allplayers.json', 'w') as outfile:
		json.dump(players, outfile, separators=(',', ":"), sort_keys=True)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		match_states(game)
	else:
		for game in games:
			match_states(game)