import braacket
import pprint
import json

ligas = [
	'teamdashsp',
	'liga_ultra_arcade_s1'
]

for liga in ligas:

	bracket = braacket.Braacket(liga)

	ranking = bracket.get_ranking()

	with open('out/'+liga+'.json', 'w') as outfile:
	  json.dump(ranking, outfile)
