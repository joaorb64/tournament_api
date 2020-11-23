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

def update_league(liga):
	print("Updating league " + liga)
	bracket = braacket.Braacket(liga)

	if not os.path.exists('out/'+liga):
		os.makedirs('out/'+liga)

	# get ranking
	ranking = bracket.get_ranking()

	with open('out/'+liga+'/ranking.json', 'w') as outfile:
		out = {
			"ranking": ranking,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)
	
	# get players
	players = bracket.get_players()

	with open('out/'+liga+'/players.json', 'w') as outfile:
		out = {
			"players": players,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)

	# get tournaments
	tournaments = bracket.get_tournaments()
	got = bracket.get_tournament_ranking_all([tournament for tournament in tournaments])

	for i, tournament in enumerate(tournaments):
		tournaments[tournament]["ranking"] = got[tournament]

		if tournaments[tournament]["ranking"] != None:
			tournaments[tournament]["player_number"] = len(tournaments[tournament]["ranking"])
		else:
			tournaments[tournament]["player_number"] = None

	with open('out/'+liga+'/tournaments.json', 'w') as outfile:
		out = {
			"tournaments": tournaments,
			"update_time": str(datetime.now())
		}
		json.dump(out, outfile, indent=4, sort_keys=True)
	
	# get league data
	league_data = bracket.get_league_data()
	league_data = update(league_data, leagues[liga])

	with open('out/'+liga+'/data.json', 'w') as outfile:
		out = league_data
		json.dump(out, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		for liga in leagues.keys():
			if liga == sys.argv[1]:
				update_league(liga)
	else:
		Parallel(n_jobs=4)(delayed(update_league)(liga) for liga in leagues.keys())