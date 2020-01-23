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

f = open('leagues.json')
json_obj = json.load(f)

for liga in json_obj.keys():

	bracket = braacket.Braacket(liga)

	with open('league_info/'+liga+'.json', 'w') as outfile:
		league = {
			"name": bracket.get_league_name()
		}
		json.dump(league, outfile)

	try:
		ranking = bracket.get_ranking()

		for player in ranking.keys():
			name = text_to_id(ranking[player]['name'])
			if not os.path.exists("player_data/"+name):
				os.makedirs("player_data/"+name)
				with open("player_data/"+name+"/data.json", 'w') as outfile:
					json.dump({}, outfile)
			else:
				if os.path.exists("player_data/"+name+"/data.json"):
					player_extra_file = open("player_data/"+name+"/data.json")
					player_extra_json = json.load(player_extra_file)
					ranking[player].update(player_extra_json)
				if os.path.exists("player_data/"+name+"/avatar.png"):
					ranking[player].update({"avatar": "player_data/"+name+"/avatar.png"})

		with open('out/'+liga+'.json', 'w') as outfile:
			json.dump(ranking, outfile)
	except:
		pass