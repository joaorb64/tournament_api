import json
import os
import unicodedata
import collections
import collections.abc
import sys

leagues = None

def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
        d[k] = update(d.get(k, {}), v)
    else:
        d[k] = v
  return d

def link_leagues(game):
  f = open("./games/"+game+'/leagues.json')
  leagues = json.load(f)

  f = open('./games/'+game+'/allplayerskins.json')
  playerSkins = json.load(f)

  mapping = {}
  allplayers = []

  print("Gen alltournaments and allmatches")

  alltournaments = {}

  for league in leagues.keys():
    f = open('out/'+game+'/'+league+'/tournaments.json')
    tournaments = json.load(f)
    alltournaments[league] = tournaments["tournaments"]

  with open('out/'+game+'/alltournaments.json', 'w') as outfile:
    json.dump(alltournaments, outfile, indent=4, sort_keys=True)

  print("Gen allplayers")

  for league in leagues.keys():
    f = open('out/'+game+'/'+league+'/players.json')
    players = json.load(f)

    for player in players["players"].items():
      my_league = league
      my_uuid = player[0]

      if my_league in alltournaments.keys():

        tournaments_sorted = sorted(alltournaments[my_league].items(), key=lambda x: x[1]["time"], reverse=True)

        for tournament in tournaments_sorted:
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
        if player[1].get("smashgg_id") is not None and player2.get("smashgg_id") is not None and \
          player[1].get("smashgg_id") == player2.get("smashgg_id"):
            found = True
        elif player[1].get("twitter") is not None and player2.get("twitter") is not None and \
          player[1].get("twitter") == player2.get("twitter"):
            print(">>>> merge twitter: "+player[1].get("twitter"))
            found = True
        elif player[1].get("braacket_account") is not None and player2.get("braacket_account") is not None and \
          player[1].get("braacket_account") == player2.get("braacket_account"):
            print(">>>> merge braacket: "+player[1].get("braacket_account"))
            found = True
        
        if found:
          # merge braacket_links
          player2["braacket_links"].append(league+":"+player[0])
          mapping[league+":"+player[0]] = i

          # merge mains
          if len(player[1].get("mains", [])) > 0 and len(player2.get("mains",[])) == 0:
            player2["mains"] = player[1].get("mains")

          # merge twitter
          if player[1].get("twitter", None) is not None and player2.get("twitter", None) is None:
            player2["twitter"] = player[1].get("twitter")

          # merge country_code
          if player[1].get("country_code", None) is not None and player2.get("country_code", None) is None:
            player2["country_code"] = player[1].get("country_code")

          # merge braacket_account
          if player[1].get("braacket_account", None) is not None and player2.get("braacket_account", None) is None:
            player2["braacket_account"] = player[1].get("braacket_account")
          break
      
      if not found:
        player[1]["braacket_links"] = [league+":"+player[0]]
        allplayers.append(player[1])
        mapping[league+":"+player[0]] = len(allplayers)-1
      
      if "smashgg_id" in player[1]:
        if str(player[1]["smashgg_id"]) in playerSkins:
          player[1]["skins"] = playerSkins[str(player[1]["smashgg_id"])]

  with open('out/'+game+'/allplayers.json', 'w') as outfile:
    json.dump({"mapping": mapping, "players": allplayers}, outfile, indent=4, sort_keys=True)

  print("Gen allleagues")

  allleagues = {}

  for league in leagues.keys():
    f = open('out/'+game+'/'+league+'/data.json')
    leaguedata = json.load(f)
    allleagues[league] = leaguedata

  with open('out/'+game+'/allleagues.json', 'w') as outfile:
    json.dump(allleagues, outfile, indent=4, sort_keys=False)

if __name__ == "__main__":
  games = os.listdir("./games")

  if len(sys.argv) >= 2:
    game = sys.argv[1]
    link_leagues(game)
  else:
    for game in games:
      link_leagues(game)