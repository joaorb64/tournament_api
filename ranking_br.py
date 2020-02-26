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

bracket = braacket.Braacket('prbth')

if not os.path.exists("out/tournament/"+'prbth'+".json"):
	with open("out/tournament/"+'prbth'+".json", 'w') as outfile:
		json.dump({}, outfile)

f = open("out/tournament/"+'prbth_override'+".json")
json_obj = json.load(f)

tournaments = bracket.get_tournaments()

for tournament in tournaments:
	if tournament == "prbth":
		continue
	tournaments[tournament]["ranking"] = bracket.get_tournament_ranking(tournament)
	tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])

update(json_obj, tournaments)

with open("out/tournament/"+'prbth'+".json", 'w') as outfile:
	json.dump(json_obj, outfile, indent=4, sort_keys=True)


players = bracket.get_players()

f = open('leagues.json')
json_obj = json.load(f)

for player in players:
	for liga in json_obj.keys():
		try:
			f_league = open('out/'+liga+'.json')
			json_league_players = json.load(f_league)
			
			for league_player in json_league_players:
				if players[player]["name"] == json_league_players[league_player]["name"]:
					players[player].update(json_league_players[league_player])
					break
		except:
			pass

	scores = []

	for tournament in tournaments:
		if player in tournaments[tournament]["ranking"]:
			rank = tournaments[tournament]["ranking"][player]["rank"]

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
				elif tournaments[tournament]["player_number"] >= 49:
					point_system = point_system_49
				elif tournaments[tournament]["player_number"] >= 33:
					point_system = point_system_33
				elif tournaments[tournament]["player_number"] >= 25:
					point_system = point_system_25
				else:
					point_system = point_system_1

			if rank in point_system:
				scores.append(point_system[rank])
	
	scores.sort(reverse=True)
	scores = scores[:10]

	players[player]["rank"] = {"prbth": {"score": sum(scores)}}

def orderByScore(a, b):
	if int(players[a]["rank"]["prbth"]["score"]) > int(players[b]["rank"]["prbth"]["score"]):
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

		player_extra_json["rank"]["prbth"] = {
			"score": players[player]["rank"]["prbth"]["score"],
			"rank": i
		}

		players[player].update(player_extra_json)

		players[player]["rank"]["prbth"]["rank"] = i

		with open("player_data/"+name+"/data.json", 'w') as outfile:
			json.dump(player_extra_json, outfile, indent=4, sort_keys=True)
		i += 1

with open('out/prbth.json', 'w') as outfile:
	json.dump(players, outfile, indent=4, sort_keys=True)