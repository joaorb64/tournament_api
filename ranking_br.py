import braacket
import pprint
import json
import os
import unicodedata
import re

def remove_accents(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def text_to_id(text):
	text = remove_accents(text)
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

###

bracket = braacket.Braacket('prbth')

if not os.path.exists("out/tournament/"+'prbth'+".json"):
	with open("out/tournament/"+'prbth'+".json", 'w') as outfile:
		json.dump({}, outfile)

f = open("out/tournament/"+'prbth'+".json")
json_obj = json.load(f)

tournaments = bracket.get_tournaments()

for tournament in tournaments:
	if tournament in json_obj:
		continue
	tournaments[tournament]["ranking"] = bracket.get_tournament_ranking(tournament)
	tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])

tournaments.update(json_obj)

with open("out/tournament/"+'prbth'+".json", 'w') as outfile:
	json.dump(tournaments, outfile, indent=4, sort_keys=True)


players = bracket.get_players()

f = open('leagues.json')
json_obj = json.load(f)

for player in players:
	for liga in json_obj.keys():
		f_league = open('out/'+liga+'.json')
		json_league_players = json.load(f_league)
		
		for league_player in json_league_players:
			if players[player]["name"] == json_league_players[league_player]["name"]:
				players[player].update(json_league_players[league_player])
				break

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
			
	players[player]["total_score"] = sum(scores)

with open('out/ranking_br.json', 'w') as outfile:
	json.dump(players, outfile)