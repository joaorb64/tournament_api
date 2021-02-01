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
		if "character_usage" in resp.keys():
			player["character_usage"] = resp["character_usage"]
		if "mains" in resp.keys():
			player["mains"] = resp["mains"]

print("")

with open('out/allplayers.json', 'w') as outfile:
	json.dump(original_players, outfile, indent=4, sort_keys=True)