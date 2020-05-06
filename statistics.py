import braacket
import pprint
import json
import os
import unicodedata
import re
import functools
import collections.abc

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
	"Pokémon Trainer": "Pokemon Trainer",
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
	"Rosalina & Luma": "Rosalina And Luma",
	"Little Mac": "Little Mac",
	"Greninja": "Greninja",
	"Mii Fighter": "Mii Brawler",
	"Mii Swordighter": "Mii Swordfighter",
	"Mii Gunner": "Mii Gunner",
	"Palutena": "Palutena",
	"PAC-MAN": "Pac Man",
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
	"Simon": "Simon",
	"Richter": "Richter",
	"King K. Rool": "King K Rool",
	"Isabelle": "Isabelle",
	"Incineroar": "Incineroar",
	"Piranha Plant": "Piranha Plant",
	"Joker": "Joker",
	"Hero": "Hero",
	"Banjo & Kazooie": "Banjo-Kazooie",
	"Terry": "Terry",
	"Byleth": "Byleth",
}
###

pprint = pprint.PrettyPrinter()

# saida final
outInfo = {}

# Linked players
# Players in BR ranking also in a local ranking
with open("out/"+'prbth'+".json") as infile:
	json_obj = json.load(infile)

	unlinked = []

	for p in json_obj["ranking"]:
		if not ("rank" in json_obj["ranking"][p].keys() and len(json_obj["ranking"][p]["rank"]) > 1):
			unlinked.append(json_obj["ranking"][p])
		
	outInfo["linkage"] = {
		"unlinked": unlinked,
		"total": len(json_obj.keys())
	}

# Players per region
with open("out/"+'prbth'+".json") as infile:
	json_obj = json.load(infile)

	playersPerRegion = {}

	for p in json_obj["ranking"]:
		if "rank" in json_obj["ranking"][p].keys():
			for liga in json_obj["ranking"][p]["rank"]:
				if "wifi" in json_obj["ranking"][p]["rank"][liga]:
					continue
				if liga != 'prbth':
					if liga in playersPerRegion:
						playersPerRegion[liga] += 1
					else:
						playersPerRegion[liga] = 1
	
	outInfo["players_per_region"] = playersPerRegion

# Score per region
with open("out/"+'prbth'+".json") as infile:
	json_obj = json.load(infile)

	scorePerRegion = {}

	for p in json_obj["ranking"]:
		if "rank" in json_obj["ranking"][p].keys():
			for liga in json_obj["ranking"][p]["rank"]:
				if liga != 'prbth' and "wifi" not in json_obj["ranking"][p]["rank"][liga]:
					if liga in scorePerRegion:
						scorePerRegion[liga] += json_obj["ranking"][p]["rank"]['prbth']["score"]
					else:
						scorePerRegion[liga] = json_obj["ranking"][p]["rank"]['prbth']["score"]
	
	outInfo["score_per_region"] = scorePerRegion

# Best of each character
with open("out/"+'prbth'+".json") as infile:
	json_obj = json.load(infile)

	def orderByRank(a, b):
		if json_obj["ranking"][a]["rank"]["prbth"]["score"] < json_obj["ranking"][b]["rank"]["prbth"]["score"]:
			return 1
		else:
			return -1
		
	ordered = list(json_obj["ranking"].keys())
	ordered.sort(key=functools.cmp_to_key(orderByRank))

	bestWithEachChar = {}

	for c in characters:
		for p in ordered:
			if "mains" in json_obj["ranking"][p].keys() and len(json_obj["ranking"][p]["mains"]) > 0:
				if json_obj["ranking"][p]["mains"][0]["name"] == characters[c]:
					bestWithEachChar[c] = json_obj["ranking"][p]
					break

	outInfo["best_player_character"] = bestWithEachChar

# Character usage
with open("out/"+'prbth'+".json") as infile:
	json_obj = json.load(infile)

	charUsage = {}

	for c in characters:
		charUsage[c] = {
			"usage": 0
		}
		for p in json_obj["ranking"]:
			if "mains" in json_obj["ranking"][p].keys() and len(json_obj["ranking"][p]["mains"]) > 0:
				if json_obj["ranking"][p]["mains"][0]["name"] == characters[c]:
					charUsage[c]["usage"] += 1
					charUsage[c]["icon"] = json_obj["ranking"][p]["mains"][0]["icon"]
		
	outInfo["char_usage"] = charUsage

with open('out/statistics.json', 'w') as outfile:
	json.dump(outInfo, outfile, indent=4, sort_keys=True)