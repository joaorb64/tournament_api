import sys
sys.path.append('../')
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

point_system_ssr = {
	"1": 400,
	"2": 300,
	"3": 220,
	"4": 150,
	"5": 100,
	"7": 70,
	"9": 50,
	"13": 25,
	"17": 10,
	"25": 5,
	"33": 1
}

point_system_sr = {
	"1": 300,
	"2": 220,
	"3": 150,
	"4": 100,
	"5": 70,
	"7": 50,
	"9": 25,
	"13": 10,
	"17": 5,
	"25": 1
}

point_system_r = {
	"1": 40,
	"2": 30,
	"3": 20,
	"4": 15,
	"5": 10,
	"7": 7,
	"9": 5,
	"13": 1
}

###

bracket = braacket.Braacket('circuitobrasileirodegranblue')

if not os.path.exists("out/tournaments.json"):
	with open("out/tournaments.json", 'w') as outfile:
		json.dump({}, outfile)

f = open("out/tournaments_override.json")
json_obj = json.load(f)

f2 = open('allplayers.json')
allplayers = json.load(f2)

tournaments = bracket.get_tournaments()

redownload_tournaments = True

if redownload_tournaments:
	got = bracket.get_tournament_ranking_all([tournament for tournament in tournaments])

	for i, tournament in enumerate(tournaments):
		tournaments[tournament]["ranking"] = got[tournament]
		tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])
	
	merged_tournaments = {}
	tournaments_list = tournaments.items()

	for tournament in tournaments_list:
		if "[R]" in tournament[1]["name"]:
			tournament[1]["tier"] = "R"

			platform = None

			if " PC " in tournament[1]["name"]:
				platform = "PC"
			if " PS4 " in tournament[1]["name"]:
				platform = "PS4"

			tournament[1]["name"] = tournament[1]["name"].replace(" PC ", " ")
			tournament[1]["name"] = tournament[1]["name"].replace(" PS4 ", " ")

			rankingCopy = copy.deepcopy(tournament[1]["ranking"])
			tournament[1]["ranking_"+platform] = rankingCopy

			tournament[1]["player_number_"+platform] = tournament[1]["player_number"]

			del tournament[1]["ranking"]
			del tournament[1]["player_number"]

			if tournament[1]["name"] not in merged_tournaments.keys():
				merged_tournaments[tournament[1]["name"]] = {}

			update(merged_tournaments[tournament[1]["name"]], tournament[1])
		else:
			if "[SR]" in tournament[1]["name"]:
				tournament[1]["tier"] = "SR"
			elif "[SSR]" in tournament[1]["name"]:
				tournament[1]["tier"] = "SSR"
			merged_tournaments[tournament[1]["name"]] = tournament[1]
	
	tournaments = merged_tournaments
else:
	with open("out/tournaments.json", 'r') as outfile:
		tournaments = json.load(outfile)

update(json_obj, tournaments)
tournaments = json_obj

with open("out/tournaments.json", 'w') as outfile:
	json.dump(json_obj, outfile, indent=4, sort_keys=True)

players = bracket.get_players()

for player in players:
	id = None
	
	if player in allplayers["mapping"]:
		id = allplayers["mapping"][player]
	else:
		allplayers["players"].append({
			"name": players[player]["name"],
			"braacket_link": [player],
			"rank": {},
			"mains": players[player]["mains"]
		})
		id = len(allplayers["players"])-1
		allplayers["mapping"][player] = id

	instance = allplayers["players"][id]

	# mains if not present
	if "mains" not in instance.keys():
		instance["mains"] = []

	if len(players[player]["mains"]) > 0 and len(instance["mains"]) == 0:
		players[player]["mains"] = copy.deepcopy(players[player]["mains"])

	scores = []
	scores_pc = []
	scores_ps4 = []
	tournaments_went = []

	for tournament in tournaments:
		if ("ranking" in tournaments[tournament].keys() and player in tournaments[tournament]["ranking"]) or \
		("ranking_PC" in tournaments[tournament].keys() and player in tournaments[tournament]["ranking_PC"]) or \
		("ranking_PS4" in tournaments[tournament].keys() and player in tournaments[tournament]["ranking_PS4"]):

			point_system = None

			if "tier" in tournaments[tournament].keys():
				if tournaments[tournament]["tier"] == "R":
					point_system = point_system_r
				elif tournaments[tournament]["tier"] == "SR":
					point_system = point_system_sr
				elif tournaments[tournament]["tier"] == "SSR":
					point_system = point_system_ssr
			
			rank_pc = None
			rank_ps4 = None
			rank = None

			if tournaments[tournament]["tier"] == "R":
				if("ranking_PC" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PC"]):
					rank_pc = tournaments[tournament]["ranking_PC"][player]["rank"]
				if("ranking_PS4" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PS4"]):
					rank_ps4 = tournaments[tournament]["ranking_PS4"][player]["rank"]
				
				if rank_pc:
					if rank_pc not in point_system:
						if int(rank_pc) < int(list(point_system.keys())[-1]):
							rank_pc = str(next(x for x in list(point_system.keys()) if int(x) > int(rank_pc)))
					
					if rank_pc in point_system:
						scores_pc.append(point_system[rank_pc])
					else:
						scores_pc.append(0)

				if rank_ps4:
					if rank_ps4 and rank_ps4 not in point_system:
						if int(rank_ps4) < int(list(point_system.keys())[-1]):
							rank_ps4 = str(next(x for x in list(point_system.keys()) if int(x) > int(rank_ps4)))

					if rank_ps4 in point_system:
						scores_ps4.append(point_system[rank_ps4])
					else:
						scores_ps4.append(0)
			else:
				rank = tournaments[tournament]["ranking"][player]["rank"]
			
				if rank not in point_system:
					if int(rank) < int(list(point_system.keys())[-1]):
						rank = str(next(x for x in list(point_system.keys()) if int(x) > int(rank)))

				if rank in point_system:
					scores.append(point_system[rank])
				else:
					scores.append(0)

			tournaments_went.append({
				"name": tournaments[tournament]["name"],
				"tier": tournaments[tournament]["tier"],
				"placing": rank,
				"placing_pc": rank_pc,
				"placing_ps4": rank_ps4,
				"points": point_system[rank] if rank in point_system else 0,
				"points_pc": point_system[rank_pc] if rank_pc in point_system else 0,
				"points_ps4": point_system[rank_ps4] if rank_ps4 in point_system else 0
			})
	
	scores.sort(reverse=True)
	scores = scores[:10]

	scores_pc.sort(reverse=True)
	scores_pc = scores_pc[:10]

	scores_ps4.sort(reverse=True)
	scores_ps4 = scores_ps4[:10]

	players[player]["tournaments"] = tournaments_went
	players[player]["tournament_points"] = scores
	players[player]["tournament_points_pc"] = scores_pc
	players[player]["tournament_points_ps4"] = scores_ps4

	players[player]["score"] = sum(scores)
	players[player]["score_pc"] = sum(scores_pc)
	players[player]["score_ps4"] = sum(scores_ps4)

for player in players:
	id = allplayers["mapping"][player]

	if not "rank" in allplayers["players"][id].keys():
		allplayers["players"][id]["rank"] = {}
	
	allplayers["players"][id]["score"] = players[player]["score"]
	allplayers["players"][id]["score_pc"] = players[player]["score_pc"]
	allplayers["players"][id]["score_ps4"] = players[player]["score_ps4"]

	allplayers["players"][id]["tournaments"] = players[player]["tournaments"]
	allplayers["players"][id]["tournament_points"] = players[player]["tournament_points"]
	allplayers["players"][id]["tournament_points_pc"] = players[player]["tournament_points_pc"]
	allplayers["players"][id]["tournament_points_ps4"] = players[player]["tournament_points_ps4"]

	i += 1

out = {"ranking": players}
out["update_time"] = str(datetime.now())

with open('out/ranking.json', 'w') as outfile:
	json.dump(out, outfile, indent=4, sort_keys=True)

# update allplayers
with open('allplayers.json', 'w') as outfile:
	json.dump(allplayers, outfile, indent=4, sort_keys=True)