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
	text = remove_accents(text.lower())
	text = re.sub('[ ]+', '_', text)
	text = re.sub('[^0-9a-zA-Z_-]', '', text)
	return text

f = open('leagues.json')
json_obj = json.load(f)

for liga in json_obj.keys():

	bracket = braacket.Braacket(liga)

	with open('league_info/'+liga+'.json', 'w') as outfile:
		league = {
			"name": bracket.get_league_name()
		}
		json.dump(league, outfile)

	ranking = bracket.get_ranking()

	for player in ranking.keys():
		name = text_to_id(ranking[player]['name'])
		if not os.path.exists("player_data/"+name):
			os.makedirs("player_data/"+name)

	with open('out/'+liga+'.json', 'w') as outfile:
	  json.dump(ranking, outfile)