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

	scores = []
	tournaments_went = []

	for tournament in tournaments:
		if ("ranking" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking"]) or \
			("ranking_PC" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PC"]) or \
			("ranking_PS4" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PS4"]):

			point_system = None

			if "tier" in tournaments[tournament].keys():
				if tournaments[tournament]["tier"] == "R":
					point_system = point_system_r
				elif tournaments[tournament]["tier"] == "SR":
					point_system = point_system_sr
				elif tournaments[tournament]["tier"] == "SSR":
					point_system = point_system_ssr
			
			rank = None
			rank_pc = None
			rank_ps4 = None
			best_console = None

			if tournaments[tournament]["tier"] == "R":
				if("ranking_PC" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PC"]):
					rank_pc = tournaments[tournament]["ranking_PC"][player]["rank"]
				if("ranking_PS4" in tournaments[tournament].keys() and
				player in tournaments[tournament]["ranking_PS4"]):
					rank_ps4 = tournaments[tournament]["ranking_PS4"][player]["rank"]
				
				if rank_pc == None:
					rank = rank_ps4
					best_console = "PS4"
				elif rank_ps4 == None:
					rank = rank_pc
					best_console = "PC"
				else:
					if int(rank_ps4) < int(rank_pc):
						rank = rank_ps4
						best_console = "PS4"
					else:
						rank = rank_pc
						best_console = "PC"
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
				"points": point_system[rank] if rank in point_system else 0
			})
	
	scores.sort(reverse=True)
	scores = scores[:10]

	players[player]["tournaments"] = tournaments_went
	players[player]["tournament_points"] = scores
	players[player]["rank"] = {"score": sum(scores)}

def orderByScore(a, b):
	if int(players[a]["rank"]["score"]) > int(players[b]["rank"]["score"]):
		return -1
	else:
		return 1
	
ordered = list(players.keys())
ordered.sort(key=functools.cmp_to_key(orderByScore))

i=1
for player in ordered:
	# Update player data
	name = text_to_id(players[player]["name"])

	if name:
		if not os.path.exists("player_data/"+name):
			os.makedirs("player_data/"+name)
			with open("player_data/"+name+"/data.json", 'w') as outfile:
				json.dump({}, outfile)
		
		player_extra_file = open("player_data/"+name+"/data.json")
		player_extra_json = json.load(player_extra_file)

		if "rank" not in player_extra_json.keys() or type(player_extra_json["rank"]) is not dict:
			player_extra_json["rank"] = {}

		player_extra_json["rank"] = {
			"score": players[player]["rank"]["score"],
			"rank": i
		}
		player_extra_json["tournaments"] = players[player]["tournaments"]
		player_extra_json["tournament_points"] = players[player]["tournament_points"]

		if "mains" in players[player].keys() and len(players[player]["mains"]) > 0 and \
			((not "mains" in player_extra_json.keys()) or len(player_extra_json["mains"]) == 0):
			player_extra_json["mains"] = players[player]["mains"]
		
		players[player].update(player_extra_json)

		players[player]["rank"]["rank"] = i

		player_extra_json["name"] = players[player]["name"]

		with open("player_data/"+name+"/data.json", 'w') as outfile:
			json.dump(player_extra_json, outfile, indent=4, sort_keys=True)
		i += 1

out = {"ranking": players}
out["update_time"] = str(datetime.utcnow())

with open('out/ranking.json', 'w') as outfile:
	json.dump(out, outfile, indent=4, sort_keys=True)
