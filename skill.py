import json
import os
import unicodedata
import collections
import collections.abc
import trueskill

def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
        d[k] = update(d.get(k, {}), v)
    else:
        d[k] = v
  return d

f = open('out/alltournaments.json')
alltournaments = json.load(f)

allmatches = []

f = open('out/allplayers.json')
allplayers = json.load(f)

for league in alltournaments:
    tournaments = sorted(list(alltournaments[league].values()), key=lambda t: t["time"])

    for tournament in tournaments:
        linkage = tournament["linkage"]
        for match in tournament["matches"]:
            myMatch = {}

            if -1 in match["participants"].values():
                continue

            p1 = next((p for p in linkage if linkage[p] == list(match["participants"].keys())[0]), None)
            p2 = next((p for p in linkage if linkage[p] == list(match["participants"].keys())[1]), None)
            winner = next((p for p in linkage if linkage[p] == match["winner"]), None)

            if p1 == None or p2 == None or winner == None:
                continue

            loser = None
            if winner == p1:
                loser = p2
            else:
                loser = p1

            p1apid = allplayers["mapping"].get(league+":"+winner)
            p2apid = allplayers["mapping"].get(league+":"+loser)

            if p1apid == None or p2apid == None:
                continue
            
            myMatch = [p1apid, p2apid]

            allmatches.append(myMatch)

players = {}

ts = trueskill.TrueSkill(draw_probability=0, mu=50.000, sigma=8.333)
ts.make_as_global()

for player in allplayers["players"]:
    if player.get("apid", None) != None:
        players[player["apid"]] = {}
        players[player["apid"]]["player"] = player
        players[player["apid"]]["rating"] = trueskill.Rating()

for match in allmatches:
    if players.get(match[0]) and players.get(match[1]):
        new_p1, new_p2 = trueskill.rate_1vs1(players[match[0]]["rating"], players[match[1]]["rating"])
        players[match[0]]["rating"] = new_p1
        players[match[1]]["rating"] = new_p2

for p in players:
    players[p]["player"]["ts"] = ts.expose(players[p]["rating"])
    players[p]["player"]["mu"] = players[p]["rating"].mu
    players[p]["player"]["sigma"] = players[p]["rating"].sigma

def mySort(p):
    return ts.expose(p["rating"])

leaderboard = sorted(players.values(), key=mySort, reverse=True)

ranking = []
for i, p in enumerate(leaderboard):
    ranking.append(p["player"])

with open('out/leaderboard.json', 'w') as outfile:
	json.dump(ranking, outfile, indent=4, sort_keys=True)

with open('out/leaderboardreadable.txt', 'w') as outfile:
    for i, p in enumerate(ranking):
        outfile.write(str(i+1) + "\t\t" + p["name"] + "\t\t\t\t\t\t" + str(p["ts"]) + "\n")

with open('out/allplayers.json', 'w') as outfile:
	json.dump(allplayers, outfile, indent=4, sort_keys=True)

with open('out/ts_env.json', 'w') as outfile:
    json.dump({
        "mu": ts.mu,
        "sigma": ts.sigma,
        "beta": ts.beta
    }, outfile, indent=4)