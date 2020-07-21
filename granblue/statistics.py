import pprint
import json
import os
import unicodedata
import re
import functools
import collections.abc

def update(d, u):
	for k, v in u.items():
			if isinstance(v, collections.abc.Mapping):
					d[k] = update(d.get(k, {}), v)
			else:
					d[k] = v
	return d

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

pprint = pprint.PrettyPrinter()

ap = open("allplayers.json")
allplayers = json.load(ap)

outInfo = {}

# Players per state
playersPerState = {}

for p in allplayers["players"]:
	if "state" in p.keys():
		if p["state"] == "":
			p["state"] = "null"
		if p["state"] in playersPerState:
			playersPerState[p["state"]] += 1
		else:
			playersPerState[p["state"]] = 1

outInfo["players_per_state"] = playersPerState

# Character usage
charUsage = {}

for p in allplayers["players"]:
	if "mains" in p.keys() and len(p["mains"]) > 0 and p["mains"][0] != "":
		if p["mains"][0] not in charUsage:
			charUsage[p["mains"][0]] = 1
		else:
			charUsage[p["mains"][0]] += 1

outInfo["char_usage"] = charUsage

league_file = open("out/ranking.json")
league_json = json.load(league_file)
league_json["statistics"] = outInfo

with open('out/ranking.json', 'w') as outfile:
	json.dump(league_json, outfile, indent=4, sort_keys=True)