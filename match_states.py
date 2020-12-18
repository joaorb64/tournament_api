import json
import os
import unicodedata
import sys
from threading import Thread

def remove_accents_lower(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

f = open('leagues.json')
leagues = json.load(f)

f = open('cities.json')
cities = json.load(f)

f = open('countries+states.json')
countries = json.load(f)

f = open('out/allplayers.json')
players = json.load(f)

def match_player_state(i, skipsize):
	while i < len(players["players"]):
		match_player_state_do(i)
		i+=skipsize

def match_player_state_do(i):
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

			if "city" in player.keys() and player["city"] is not None:
				# State explicit?
				split = player["city"].split(" ")

				for part in split:
					state = next(
						(st for st in country["states"] if remove_accents_lower(st["state_code"]) == remove_accents_lower(part)),
						None
					)
					if state is not None:
						player["state"] = state["state_code"]
						break

				if "state" not in player.keys() or player["state"] is None:
					# no, so get by City
					city = next(
						(c for c in cities if remove_accents_lower(c["name"]) == remove_accents_lower(player["city"])
						and c["country_code"] == player["country_code"]),
						None
					)

					if city is not None:
						player["state"] = city["state_code"]
	return
print("")

threads = []
thread_number = 8

for i in range(thread_number):
	thread = Thread(target=match_player_state, args=[i, thread_number])
	thread.daemon = True
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()

with open('out/allplayers.json', 'w') as outfile:
	json.dump(players, outfile, indent=4, sort_keys=True)