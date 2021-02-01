import braacket
import pprint
import json
import os
import unicodedata
import re
import copy
from datetime import datetime, tzinfo
import collections
import sys
from joblib import Parallel, delayed
import get_smashgg_tournament_data as gg

f = open('leagues.json')
leagues = json.load(f)

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

def update_league(liga, smashgg_key_id):
	print("Updating league " + liga)
	bracket = braacket.Braacket(liga)

	if not os.path.exists('out/'+liga):
		os.makedirs('out/'+liga)

	previous_ranking = None
	
	try:
		with open('out/'+liga+'/ranking.json', 'r') as infile:
			previous_ranking = json.load(infile)
	except Exception as e:
		print(e)
	
	# get league data
	league_data = bracket.get_league_data()
	league_data = update(league_data, leagues[liga])

	with open('out/'+liga+'/data.json', 'w') as outfile:
		out = league_data
		json.dump(out, outfile, indent=4, sort_keys=True)
	
	# get league players
	players = bracket.get_players()

	with open('out/'+liga+'/players.json', 'w') as outfile:
		out = {
			"players": players,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)
	
	# get ranking info
	ranking_info = bracket.get_ranking_info()

	try:
		if("update_time" in ranking_info.keys() and "update_time" in previous_ranking["ranking"].keys()):
			if ranking_info["update_time"] == previous_ranking["ranking"]["update_time"]:
				print("Ranking unchanged")
				return
	except Exception as e:
		print(e)

	# get ranking
	ranking = {}
	ranking["ranking"] = bracket.get_ranking()
	ranking.update(ranking_info)

	with open('out/'+liga+'/ranking.json', 'w') as outfile:
		out = {
			"ranking": ranking,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)

	# get tournaments
	previous_tournaments = None

	try:
		with open('out/'+liga+'/tournaments.json', 'r') as infile:
			previous_tournaments = json.load(infile)
	except Exception as e:
		print(e)

	tournaments = bracket.get_tournaments()

	for i, tournament in enumerate(tournaments):
		if previous_tournaments and previous_tournaments["tournaments"]:
			if tournament in previous_tournaments["tournaments"].keys():
				previous_tournaments["tournaments"][tournament]["name"] = tournaments[tournament]["name"]
				previous_tournaments["tournaments"][tournament]["time"] = tournaments[tournament]["time"]
				tournaments[tournament] = previous_tournaments["tournaments"][tournament]
				print("Tournament known. Still, linkage could have changed.")
				ranking_get = bracket.get_tournament_ranking(tournament)
				if ranking_get is not None:
					# copy smashgg ids we got before
					for p in tournaments[tournament]["ranking"]:
						if "smashgg_id" in tournaments[tournament]["ranking"][p] and p in ranking_get["ranking"]:
							ranking_get["ranking"][p]["smashgg_id"] = tournaments[tournament]["ranking"][p]["smashgg_id"]
					tournaments[tournament]["ranking"] = ranking_get["ranking"]
					tournaments[tournament]["linkage"] = ranking_get["linkage"]
				else:
					print("Could not get tournament? - "+tournament)
				continue

		tournaments[tournament]["link"] = bracket.get_tournament_link(tournament)
		
		ranking_get = bracket.get_tournament_ranking(tournament)
		matches_get = bracket.get_tournament_matches(tournament)

		if ranking_get is not None:
			tournaments[tournament]["ranking"] = ranking_get["ranking"]
			tournaments[tournament]["linkage"] = ranking_get["linkage"]
		else:
			tournaments[tournament]["ranking"] = {}
			tournaments[tournament]["linkage"] = {}

		if tournaments[tournament]["ranking"] != None:
			tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])
		else:
			tournaments[tournament]["player_number"] = None
		
		if matches_get is not None:
			tournaments[tournament]["matches"] = matches_get
		else:
			tournaments[tournament]["matches"] = []
		
		gg.get_smashgg_tournament_info(tournaments[tournament], (smashgg_key_id)%len(gg.SMASHGG_KEYS))

	with open('out/'+liga+'/tournaments.json', 'w') as outfile:
		out = {
			"tournaments": tournaments,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		for liga in leagues.keys():
			if liga == sys.argv[1]:
				update_league(liga, 0)
	else:
		Parallel(n_jobs=len(gg.SMASHGG_KEYS))(delayed(update_league)(liga, i) for i, liga in enumerate(leagues.keys()))