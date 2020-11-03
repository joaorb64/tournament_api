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

f2 = open('allplayers.json')
allplayers = json.load(f2)

alltournaments = {}

for liga in json_obj.keys():
	bracket = braacket.Braacket(liga)

	with open('league_info/'+liga+'.json', 'w') as outfile:
		league = bracket.get_league_data()
		league.update(json_obj[liga])
		json.dump(league, outfile)
	
	ranking = bracket.get_ranking()

	if ranking != None and "ranking" in ranking.keys():
		for player in ranking["ranking"].keys():
			id = None
			unlinked = False

			if liga+":"+player in allplayers["mapping"].keys():
				id = allplayers["mapping"][liga+":"+player]
			else:
				allplayers["players"].append({})
				id = len(allplayers["players"])-1
				allplayers["mapping"][liga+":"+player] = id
				unlinked = True

			instance = allplayers["players"][id]

			if unlinked:
				instance["unlinked"] = True

			# name for new players
			if "name" not in instance.keys():
				instance["name"] = ranking["ranking"][player]["name"]
			
			# braacket link for new players
			if "braacket_links" not in instance.keys():
				instance["braacket_links"] = []
				instance["braacket_links"].append(liga+":"+player)

			# rank
			if "rank" not in instance.keys():
				instance["rank"] = {}

			instance["rank"].update(ranking["ranking"][player]["rank"])

			if "wifi" in json_obj[liga].keys():
				instance["rank"][liga]["wifi"] = True

			# mains if not present
			if "mains" not in instance.keys() or (len(instance["mains"]) == 1 and len(instance["mains"][0]) == 0):
				instance["mains"] = []

			if len(ranking["ranking"][player]["mains"]) > 0 and len(instance["mains"]) == 0:
				instance["mains"] = copy.deepcopy(ranking["ranking"][player]["mains"])

			# twitter if on braacket but not on spreadsheet
			if ("twitter" not in instance.keys() or len(instance["twitter"]) == 0):
				if ("twitter" in ranking["ranking"][player].keys() and len(ranking["ranking"][player]["twitter"]) > 0):
					instance["twitter"] = ranking["ranking"][player]["twitter"]
			
			# image avatar... dropped?
			#if os.path.exists("player_data/"+name+"/avatar.png"):
			#	ranking["ranking"][player].update({"avatar": "player_data/"+name+"/avatar.png"})
	
	out = ranking
	out["update_time"] = str(datetime.now())

	# get tournaments
	tournaments = bracket.get_tournaments()
	got = bracket.get_tournament_ranking_all([tournament for tournament in tournaments])

	for i, tournament in enumerate(tournaments):
		tournaments[tournament]["ranking"] = got[tournament]

		if tournaments[tournament]["ranking"] != None:
			tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])
		else:
			tournaments[tournament]["player_number"] = None

	out["tournaments"] = tournaments

	alltournaments[liga] = tournaments

	with open('alltournaments.json', 'w') as outfile:
		json.dump(alltournaments, outfile, indent=4, sort_keys=True)

	# league out file
	with open('out/'+liga+'.json', 'w') as outfile:
		json.dump(out, outfile, indent=4, sort_keys=True)

	# update allplayers
	with open('allplayers.json', 'w') as outfile:
		json.dump(allplayers, outfile, indent=4, sort_keys=True)