import braacket
import pprint
import json
import os
import unicodedata
import re
import functools
import collections.abc
import copy
from datetime import datetime

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

point_system_65 = {
	"1": 75,
	"2": 60,
	"3": 50,
	"4": 35,
	"5": 27,
	"7": 20,
	"9": 16,
	"13": 13,
	"17": 10,
	"25": 7,
	"33": 4,
	"49": 2,
	"65": 1
}

point_system_49 = {
	"1": 60,
	"2": 50,
	"3": 35,
	"4": 27,
	"5": 20,
	"7": 16,
	"9": 13,
	"13": 10,
	"17": 7,
	"25": 4,
	"33": 2,
	"49": 1
}

point_system_33 = {
	"1": 50,
	"2": 35,
	"3": 27,
	"4": 20,
	"5": 16,
	"7": 13,
	"9": 10,
	"13": 7,
	"17": 4,
	"25": 2,
	"33": 1
}

point_system_25 = {
	"1": 35,
	"2": 27,
	"3": 20,
	"4": 16,
	"5": 13,
	"7": 10,
	"9": 7,
	"13": 4,
	"17": 2,
	"25": 1
}

point_system_1 = {
	"1": 30,
	"2": 20,
	"3": 16,
	"4": 13,
	"5": 10,
	"7": 7,
	"9": 4,
	"13": 2,
	"17": 1
}

###

f = open("out/tournament/"+'prbth_override'+".json")
tournament_override = json.load(f)

f2 = open('allplayers.json')
allplayers = json.load(f2)

f3 = open('alltournaments.json')
alltournaments = json.load(f3)

update(tournament_override, alltournaments["prbth"])
alltournaments["prbth"] = tournament_override

players = []

with open("out/tournament/"+'prbth'+".json", 'w') as outfile:
	json.dump(alltournaments["prbth"], outfile, indent=4, sort_keys=True)

for player in allplayers["mapping"]:
	if not player.startswith("prbth"):
		continue

	id = allplayers["mapping"][player]
	instance = allplayers["players"][id]

	scores = []
	tournaments_went = []

	tournaments = alltournaments["prbth"]

	prbth_id = player.split(":")[1]

	for tournament in tournaments:
		if prbth_id in tournaments[tournament]["ranking"]:
			rank = tournaments[tournament]["ranking"][prbth_id]["rank"]

			point_system = None

			if "rank" in tournaments[tournament].keys():
				if tournaments[tournament]["rank"] == "S":
					point_system = point_system_65
				elif tournaments[tournament]["rank"] == "A":
					point_system = point_system_49
				elif tournaments[tournament]["rank"] == "B":
					point_system = point_system_33
				elif tournaments[tournament]["rank"] == "C":
					point_system = point_system_25
				else:
					point_system = point_system_1
			else:
				if tournaments[tournament]["player_number"] >= 65:
					point_system = point_system_65
					tournaments[tournament]["rank"] = "S"
				elif tournaments[tournament]["player_number"] >= 49:
					point_system = point_system_49
					tournaments[tournament]["rank"] = "A"
				elif tournaments[tournament]["player_number"] >= 33:
					point_system = point_system_33
					tournaments[tournament]["rank"] = "B"
				elif tournaments[tournament]["player_number"] >= 25:
					point_system = point_system_25
					tournaments[tournament]["rank"] = "C"
				else:
					point_system = point_system_1
					tournaments[tournament]["rank"] = "D"
			
			if rank not in point_system:
				if int(rank) < int(list(point_system.keys())[-1]):
					rank = str(next(x for x in list(point_system.keys()) if int(x) > int(rank)))

			if rank in point_system:
				scores.append(point_system[rank])
			else:
				scores.append(0)

			tournaments_went.append({
				"name": tournaments[tournament]["name"],
				"rank": tournaments[tournament]["rank"],
				"placing": tournaments[tournament]["ranking"][prbth_id]["rank"],
				"points": point_system[rank] if rank in point_system else 0
			})
	
	scores.sort(reverse=True)
	scores = scores[:10]

	instance["tournaments"] = tournaments_went
	instance["tournament_points"] = scores
	instance["rank"]["prbth"] = {"score": sum(scores)}

	players.append(player)

def orderByScore(a, b):
	p1 = allplayers["players"][int(allplayers["mapping"][a])]
	p2 = allplayers["players"][int(allplayers["mapping"][b])]
	if int(p1["rank"]["prbth"]["score"]) > int(p2["rank"]["prbth"]["score"]):
		return -1
	else:
		return 1
	
ordered = players
ordered.sort(key=functools.cmp_to_key(orderByScore))

i=1
for player in ordered:
	id = allplayers["mapping"][player]

	if not "rank" in allplayers["players"][id].keys():
		allplayers["players"][id]["rank"] = {}
	
	allplayers["players"][id]["rank"]["prbth"]["rank"] = i

	i += 1

with open('alltournaments.json', 'w') as outfile:
	json.dump(alltournaments, outfile, indent=4, sort_keys=True)

# update allplayers
with open('allplayers.json', 'w') as outfile:
	json.dump(allplayers, outfile, indent=4, sort_keys=True)