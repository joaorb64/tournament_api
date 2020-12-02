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
	"Mii Swordfighter": "Mii Swordfighter",
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
	"Min Min": "Min Min",
	"Steve": "Steve"
}
###

pprint = pprint.PrettyPrinter()

f = open('leagues.json')
ligas = json.load(f)

ap = open("out/allplayers.json")
allplayers = json.load(ap)

# League statistics
for liga in ligas:
	f = open('out/'+liga+'/players.json')
	league_players = json.load(f)

	f = open('out/'+liga+'/ranking.json')
	league_ranking = json.load(f)

	if league_ranking.get("ranking") == None:
		continue
	if league_ranking.get("ranking").get("ranking") == None:
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

		if p["state"] in playersPerState:
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

	for c in characters:
		for p in ordered:
			if "mains" in p.keys() and len(p["mains"]) > 0:
				if p["mains"][0] == characters[c]:
					bestWithEachChar[c] = p

					if "bestPlayerCharacter" not in p.keys():
						p["bestPlayerCharacter"] = {}
						allplayers["players"][p["apid"]]["bestPlayerCharacter"] = {}
					
					p["bestPlayerCharacter"][liga] = [c, characters[c]]
					allplayers["players"][p["apid"]]["bestPlayerCharacter"][liga] = [c, characters[c]]

					break

	outInfo["best_player_character"] = bestWithEachChar

	# Character usage
	charUsage = {}

	for c in characters:
		charUsage[c] = {
			"usage": 0,
			"secondary": 0,
			"name": characters[c]
		}
		for p in league_players["players"].values():
			if "mains" in p.keys() and len(p["mains"]) > 0:
				if p["mains"][0] == characters[c]:
					charUsage[c]["usage"] += 1
			if "mains" in p.keys() and len(p["mains"]) > 1:
				for main in p["mains"][1:]:
					if main == characters[c]:
						charUsage[c]["secondary"] += 1
	
	outInfo["char_usage"] = charUsage

	with open('out/'+liga+'/statistics.json', 'w') as outfile:
		json.dump(outInfo, outfile, indent=4, sort_keys=True)

# General statistics
outInfo = {}

outInfo["player_number"] = len(allplayers["players"])

# Character usage
charUsage = {}

for c in characters:
	charUsage[c] = {
		"usage": 0,
		"secondary": 0,
		"name": characters[c]
	}
	for p in allplayers["players"]:
		if "mains" in p.keys() and len(p["mains"]) > 0:
			if p["mains"][0] == characters[c]:
				charUsage[c]["usage"] += 1
		if "mains" in p.keys() and len(p["mains"]) > 1:
			for main in p["mains"][1:]:
				if main == characters[c]:
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

with open('out/statistics.json', 'w') as outfile:
	json.dump(outInfo, outfile, indent=4, sort_keys=True)

with open('out/allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)