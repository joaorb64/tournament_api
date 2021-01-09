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

print("Gen alltournaments and allmatches")

alltournaments = {}
allmatches = {}

for league in leagues.keys():
  f = open('out/'+league+'/tournaments.json')
  tournaments = json.load(f)
  alltournaments[league] = tournaments["tournaments"]

with open('out/alltournaments.json', 'w') as outfile:
  json.dump(alltournaments, outfile, indent=4, sort_keys=True)

print("Gen allplayers")

allplayers_previous = None

try:
  f = open('out/allplayers.json')
  allplayers_previous = json.load(f)
except Exception as e:
  print(e)

for league in leagues.keys():
  f = open('out/'+league+'/players.json')
  players = json.load(f)

  for player in players["players"].items():
    my_league = league
    my_uuid = player[0]

    if my_league in alltournaments.keys():
      for tournament in alltournaments[my_league].items():
        # Not on smashgg
        if "link" not in tournament[1].keys():
          continue

        if my_uuid in tournament[1]["linkage"]:
          id_in_tournament = tournament[1]["linkage"][my_uuid]

          if "smashgg_id" in tournament[1]["ranking"][id_in_tournament].keys():
            player[1]["smashgg_id"] = tournament[1]["ranking"][id_in_tournament]["smashgg_id"]
            break

    # Either join to existing player or create a new entry
    found = False
    
    for i, player2 in enumerate(allplayers):
      if player[1].get("smashgg_id") is not None and player2.get("smashgg_id") is not None:
        if player[1].get("smashgg_id") == player2.get("smashgg_id"):
          found = True
          player2["braacket_links"].append(league+":"+player[0])
          mapping[league+":"+player[0]] = i
          if len(player[1].get("mains", [])) > 0 and len(player2.get("mains",[])) == 0:
            player2["mains"] = player[1].get("mains")
          break
    
    if not found:
      player[1]["braacket_links"] = [league+":"+player[0]]
      allplayers.append(player[1])
      mapping[league+":"+player[0]] = len(allplayers)-1

with open('out/allplayers.json', 'w') as outfile:
  json.dump({"mapping": mapping, "players": allplayers}, outfile, indent=4, sort_keys=True)

print("Gen allleagues")

allleagues = {}

for league in leagues.keys():
  f = open('out/'+league+'/data.json')
  leaguedata = json.load(f)
  allleagues[league] = leaguedata

with open('out/allleagues.json', 'w') as outfile:
  json.dump(allleagues, outfile, indent=4, sort_keys=False)