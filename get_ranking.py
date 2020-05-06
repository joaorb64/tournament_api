import braacket
import pprint
import json
import os
import unicodedata
import re
import copy
from datetime import datetime, tzinfo

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

f = open('leagues.json')
json_obj = json.load(f)

for liga in json_obj.keys():

	if liga == "prbth":
		continue

	bracket = braacket.Braacket(liga)

	with open('league_info/'+liga+'.json', 'w') as outfile:
		league = bracket.get_league_data()
		league.update(json_obj[liga])
		json.dump(league, outfile)
	
	ranking = bracket.get_ranking()

	if ranking != None:
		for player in ranking.keys():
			name = text_to_id(ranking[player]['name'])

			if name:
				if not os.path.exists("player_data/"+name):
					os.makedirs("player_data/"+name)
					with open("player_data/"+name+"/data.json", 'w') as outfile:
						json.dump({}, outfile)

				player_extra_file = open("player_data/"+name+"/data.json")
				player_extra_json = json.load(player_extra_file)

				if "rank" not in player_extra_json.keys() or type(player_extra_json["rank"]) is not dict:
					player_extra_json["rank"] = {}

				file_rank = player_extra_json["rank"].copy()
				
				player_extra_json.update(ranking[player])

				player_extra_json["rank"] = file_rank

				player_extra_json["rank"].update(ranking[player]["rank"])

				if "wifi" in json_obj[liga].keys():
					player_extra_json["rank"][liga]["wifi"] = True

				if len(ranking[player]["mains"]) > 0:
					player_extra_json["mains"] = ranking[player]["mains"]

				if "twitter" in ranking[player]:
					player_extra_json["twitter"] = ranking[player]["twitter"]

				ranking[player] = player_extra_json
				
				if os.path.exists("player_data/"+name+"/avatar.png"):
					ranking[player].update({"avatar": "player_data/"+name+"/avatar.png"})

				with open("player_data/"+name+"/data.json", 'w') as outfile:
					json.dump(ranking[player], outfile, indent=4, sort_keys=True)
	
	out = {"ranking": ranking}
	out["update_time"] = str(datetime.utcnow())

	with open('out/'+liga+'.json', 'w') as outfile:
		json.dump(out, outfile, indent=4, sort_keys=True)
