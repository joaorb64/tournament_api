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

ap = open("allplayers.json")
allplayers = json.load(ap)

for liga in ligas:
	outInfo = {}

	# somente para ligas BR
	if ligas[liga]["state"] == "BR":
		# Players per league
		playersPerLeague = {}

		for p in allplayers["players"]:
			if "rank" in p.keys():
				if liga not in p["rank"].keys():
					continue
				for pliga in p["rank"]:
					if "wifi" in p["rank"][pliga]:
						continue
					if pliga != liga and pliga in ligas.keys() and ligas[pliga]["state"] != "BR":
						if pliga in playersPerLeague:
							playersPerLeague[pliga] += 1
						else:
							playersPerLeague[pliga] = 1
		
		outInfo["players_per_league"] = playersPerLeague

		# Score per league
		scorePerLeague = {}

		for p in allplayers["players"]:
			if "rank" in p.keys() and liga in p["rank"]:
				if liga not in p["rank"].keys():
					continue
				for pliga in p["rank"]:
					if "wifi" in p["rank"][pliga]:
						continue
					if pliga != liga and pliga in ligas.keys() and ligas[pliga]["state"] != "BR":
						if pliga in scorePerLeague:
							scorePerLeague[pliga]["score"] += float(p["rank"][liga]["score"])
						else:
							scorePerLeague[pliga] = {"score": float(p["rank"][liga]["score"])}
		
		for pliga in scorePerLeague:
			scorePerLeague[pliga]["average"] = float(scorePerLeague[pliga]["score"]) / float(playersPerLeague[pliga])
		
		outInfo["score_per_league"] = scorePerLeague

		# Players per state
		playersPerState = {}

		for p in allplayers["players"]:
			if "rank" in p.keys():
				if liga not in p["rank"].keys():
					continue
				if "state" in p.keys():
					if p["state"] == "":
						p["state"] = "null"
					if p["state"] in playersPerState:
						playersPerState[p["state"]] += 1
					else:
						playersPerState[p["state"]] = 1
		
		outInfo["players_per_state"] = playersPerState

	# Best of each character
	def orderByRank(a, b):
		if int(a["rank"][liga]["score"]) < int(b["rank"][liga]["score"]):
			return 1
		else:
			return -1
			
	ordered = [p for p in allplayers["players"] if "rank" in p and liga in p["rank"] and len(p["mains"]) > 0]
	ordered.sort(key=functools.cmp_to_key(orderByRank))

	bestWithEachChar = {}

	for c in characters:
		for p in ordered:
			if liga not in p["rank"].keys():
					continue
			if "mains" in p.keys() and len(p["mains"]) > 0:
				if p["mains"][0] == characters[c]:
					bestWithEachChar[c] = p

					if "bestPlayerCharacter" not in p.keys():
						p["bestPlayerCharacter"] = {}
					
					p["bestPlayerCharacter"][liga] = [c, characters[c]]

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
		for p in allplayers["players"]:
			if "rank" in p.keys():
				if liga not in p["rank"].keys():
						continue
				if "mains" in p.keys() and len(p["mains"]) > 0:
					if p["mains"][0] == characters[c]:
						charUsage[c]["usage"] += 1
				if "mains" in p.keys() and len(p["mains"]) > 1:
					for main in p["mains"][1:]:
						if main == characters[c]:
							charUsage[c]["secondary"] += 1
		
	outInfo["char_usage"] = charUsage

	league_file = open("out/"+liga+".json")
	league_json = json.load(league_file)
	league_json["statistics"] = outInfo

	with open('out/'+liga+'.json', 'w') as outfile:
		json.dump(league_json, outfile, indent=4, sort_keys=True)

with open('allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)