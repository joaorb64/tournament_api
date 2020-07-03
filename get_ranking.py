import braacket
import pprint
import json
import os
import unicodedata
import re
import copy
from datetime import datetime, tzinfo
import collections

def remove_accents(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def update(d, u):
	for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
					d[k] = update(d.get(k, {}), v)
			else:
					d[k] = v
	return d

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

				player_extra_json_original = copy.deepcopy(player_extra_json)

				if "rank" not in player_extra_json.keys() or type(player_extra_json["rank"]) is not dict:
					player_extra_json["rank"] = {}

				file_rank = player_extra_json["rank"].copy()
				file_mains = copy.deepcopy(player_extra_json["mains"]) if "mains" in player_extra_json.keys() else []

				update(player_extra_json, ranking[player])

				player_extra_json["braacket_link"].update(ranking[player]["braacket_link"])

				player_extra_json["rank"] = file_rank

				player_extra_json["rank"].update(ranking[player]["rank"])

				if "wifi" in json_obj[liga].keys():
					player_extra_json["rank"][liga]["wifi"] = True

				if "twitter" in ranking[player]:
					player_extra_json["twitter"] = ranking[player]["twitter"]

				ranking[player] = player_extra_json

				if len(ranking[player]["mains"]) > 0:
					player_extra_json["mains"] = ranking[player]["mains"]
				else:
					ranking[player]["mains"] = copy.deepcopy(file_mains)
				
				if os.path.exists("player_data/"+name+"/avatar.png"):
					ranking[player].update({"avatar": "player_data/"+name+"/avatar.png"})

				with open("player_data/"+name+"/data.json", 'w') as outfile:
					json.dump(ranking[player], outfile, indent=4, sort_keys=True)
	
	out = {"ranking": ranking}
	out["update_time"] = str(datetime.utcnow())

	with open('out/'+liga+'.json', 'w') as outfile:
		json.dump(out, outfile, indent=4, sort_keys=True)

	ap_file = open('allplayers.json')
	ap = json.load(ap_file)

	for p in out["ranking"]:
		if p in ap["mapping"]:
			id = ap["mapping"][p]

			if "ranking" not in ap["players"][id]:
				ap["players"][id]["ranking"] = {}

			update(ap["players"][id]["ranking"], out["ranking"][p]["rank"])

	with open('allplayers.json', 'w') as outfile:
		json.dump(ap, outfile, indent=4, sort_keys=True)