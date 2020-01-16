import braacket
import pprint
import json

f = open('leagues.json')
json_obj = json.load(f)

for liga in json_obj['leagues']:

	bracket = braacket.Braacket(liga)

	with open('league_info/'+liga+'.json', 'w') as outfile:
		league = {
			"name": bracket.get_league_name()
		}
		json.dump(league, outfile)

	ranking = bracket.get_ranking()

	with open('out/'+liga+'.json', 'w') as outfile:
	  json.dump(ranking, outfile)
