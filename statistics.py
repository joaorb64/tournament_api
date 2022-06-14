import braacket
import pprint
import json
import os
import unicodedata
import re
import functools
import collections.abc
import sys

def update(d, u):
	for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
					d[k] = update(d.get(k, {}), v)
			else:
					d[k] = v
	return d

def remove_accents(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def text_to_id(text):
	text = remove_accents(text)
	text = text.replace("@", "_At_")
	text = text.replace("~", "_Tilde_")
	text = re.sub('[ ]+', '_', text)
	text = re.sub('[^0-9a-zA-Z_-]', '', text)
	return text

pprint = pprint.PrettyPrinter()

def statistics(game):
	f = open('./games/'+game+'/leagues.json')
	ligas = json.load(f)

	ap = open("./out/"+game+"/allplayers.json")
	allplayers = json.load(ap)

	f = open('./games/'+game+'/charnames_smashgg_to_braacket.json')
	characters = json.load(f)

	f = open('./games/'+game+'/assetconfig.json')
	asset_config = json.load(f)

	# League statistics
	for liga in ligas:
		f = open('./out/'+game+'/'+liga+'/players.json')
		league_players = json.load(f)

		f = open('./out/'+game+'/'+liga+'/ranking.json')
		league_ranking = json.load(f)

		if league_ranking.get("ranking", {}).get("ranking") == None:
			continue

		# build object with centered data
		for p in league_players["players"]:
			if p in league_ranking["ranking"]["ranking"].keys():
				apid = allplayers["mapping"][liga+":"+p]
				league_players["players"][p] = allplayers["players"][apid]
				league_players["players"][p]["rank"] = league_ranking["ranking"]["ranking"][p]["rank"]
				league_players["players"][p]["apid"] = apid

		outInfo = {}

		# Total number of players
		outInfo["player_number"] = len(league_players["players"])

		# Players per state and country
		playersPerState = {}
		playersPerCountry = {}

		for p in league_players["players"].values():
			if "state" not in p.keys() or p["state"] == "":
				p["state"] = "null"
			if "country_code" not in p.keys() or p["country_code"] == "":
				p["country_code"] = "null"
			
			# state
			canonicalState = ""
			if p["country_code"] == "null" or p["state"] == "null":
				canonicalState = "null"
			else:
				canonicalState = p["country_code"]+"_"+p["state"]

			if canonicalState in playersPerState:
				playersPerState[canonicalState] += 1
			else:
				playersPerState[canonicalState] = 1
			
			# country
			if p["country_code"] in playersPerCountry:
				playersPerCountry[p["country_code"]] += 1
			else:
				playersPerCountry[p["country_code"]] = 1
		
		outInfo["players_per_state"] = playersPerState
		outInfo["players_per_country"] = playersPerCountry

		# Best of each character
		def orderByRank(a, b):
			if int(a["rank"]) > int(b["rank"]):
				return 1
			else:
				return -1
				
		ordered = [p for p in league_players["players"].values() if "rank" in p and len(p["mains"]) > 0]
		ordered.sort(key=functools.cmp_to_key(orderByRank))

		bestWithEachChar = {}

		for c in [a["codename"] for a in asset_config["character_to_codename"].values()]:
			for p in ordered:
				if "mains" in p.keys() and len(p["mains"]) > 0:
					if p["mains"][0] == c:
						bestWithEachChar[c] = p

						if "bestPlayerCharacter" not in p.keys():
							p["bestPlayerCharacter"] = {}
							allplayers["players"][p["apid"]]["bestPlayerCharacter"] = {}
						
						p["bestPlayerCharacter"][liga] = c
						allplayers["players"][p["apid"]]["bestPlayerCharacter"][liga] = c

						break

		outInfo["best_player_character"] = bestWithEachChar

		# Character usage
		charUsage = {}

		for c in [a["codename"] for a in asset_config["character_to_codename"].values()]:
			charUsage[c] = {
				"usage": 0,
				"secondary": 0
			}
			for p in league_players["players"].values():
				if "mains" in p.keys() and len(p["mains"]) > 0:
					if p["mains"][0] == c:
						charUsage[c]["usage"] += 1
				if "mains" in p.keys() and len(p["mains"]) > 1:
					for main in p["mains"][1:]:
						if main == c:
							charUsage[c]["secondary"] += 1
		
		outInfo["char_usage"] = charUsage

		with open('./out/'+game+'/'+liga+'/statistics.json', 'w') as outfile:
			json.dump(outInfo, outfile, indent=4, sort_keys=True)

	# General statistics
	outInfo = {}

	outInfo["player_number"] = len(allplayers["players"])

	# Character usage
	charUsage = {}

	for c in [a["codename"] for a in asset_config["character_to_codename"].values()]:
		charUsage[c] = {
			"usage": 0,
			"secondary": 0
		}
		for p in allplayers["players"]:
			if "mains" in p.keys() and len(p["mains"]) > 0:
				if p["mains"][0] == c:
					charUsage[c]["usage"] += 1
			if "mains" in p.keys() and len(p["mains"]) > 1:
				for main in p["mains"][1:]:
					if main == c:
						charUsage[c]["secondary"] += 1
		
	outInfo["char_usage"] = charUsage

	# Players per country
	playersPerCountry = {}

	for p in allplayers["players"]:
		if "state" not in p.keys() or p["state"] == "":
			p["state"] = "null"
		if "country_code" not in p.keys() or p["country_code"] == "":
			p["country_code"] = "null"
		
		# country
		if p["country_code"] in playersPerCountry:
			playersPerCountry[p["country_code"]] += 1
		else:
			playersPerCountry[p["country_code"]] = 1

	outInfo["players_per_country"] = playersPerCountry

	# Number of leagues
	outInfo["league_number"] = len(ligas)

	with open('./out/'+game+'/statistics.json', 'w') as outfile:
		json.dump(outInfo, outfile, indent=4, sort_keys=True)

	with open('./out/'+game+'/allplayers.json', 'w') as outfile:
		json.dump(allplayers, outfile, separators=(',', ":"), sort_keys=True)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		statistics(game)
	else:
		for game in games:
			statistics(game)