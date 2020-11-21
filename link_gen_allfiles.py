import json
import os
import unicodedata
import collections
import collections.abc

def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
        d[k] = update(d.get(k, {}), v)
    else:
        d[k] = v
  return d

f = open('leagues.json')
leagues = json.load(f)

mapping = {}
allplayers = []

print("Gen allplayers")

for league in leagues.keys():
  f = open('out/'+league+'/players.json')
  players = json.load(f)

  for player in players["players"].items():
    found = False
    
    for i, player2 in enumerate(allplayers):
      if player[1].get("smashgg_id") is not None and player2.get("smashgg_id") is not None:
        if player[1].get("smashgg_id") == player2.get("smashgg_id"):
          found = True
          player2["braacket_links"].append(league+":"+player[0])
          mapping[league+":"+player[0]] = i
          break
    
    if not found:
      player[1]["braacket_links"] = [league+":"+player[0]]
      allplayers.append(player[1])
      mapping[league+":"+player[0]] = len(allplayers)-1

with open('out/allplayers.json', 'w') as outfile:
  json.dump({"mapping": mapping, "players": allplayers}, outfile, indent=4, sort_keys=True)

print("Gen alltournaments")

alltournaments = {}

for league in leagues.keys():
  f = open('out/'+league+'/tournaments.json')
  tournaments = json.load(f)
  alltournaments[league] = tournaments["tournaments"]

with open('out/alltournaments.json', 'w') as outfile:
  json.dump(alltournaments, outfile, indent=4, sort_keys=True)

print("Gen allleagues")

allleagues = {}

for league in leagues.keys():
  f = open('out/'+league+'/data.json')
  leaguedata = json.load(f)
  allleagues[league] = leaguedata

with open('out/allleagues.json', 'w') as outfile:
  json.dump(allleagues, outfile, indent=4, sort_keys=False)