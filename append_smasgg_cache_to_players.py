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

def append_data(game):
	print("Game: "+game)

	f = open('./games/'+game+'/leagues.json')
	leagues = json.load(f)

	f = open('./out/'+game+'/smashgg_cache.json')
	smashgg_cache = json.load(f)

	f = open('./out/'+game+'/allplayers.json')
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
				if resp["location"]["state"] is not None:
					player["state"] = resp["location"]["state"]

			if resp["images"] is not None:
				for image in resp["images"]:
					if image["type"] == "profile":
						player["smashgg_image"] = image["url"]

			# character usage, mains
			if "character_usage" in resp.keys():
				player["character_usage"] = resp["character_usage"]
			if "mains" in resp.keys():
				player["mains"] = resp["mains"]

	print("")

	with open('./out/'+game+'/allplayers.json', 'w') as outfile:
		json.dump(original_players, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		append_data(game)
	else:
		for game in games:
			append_data(game)