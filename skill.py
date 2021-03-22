import json
import os
import unicodedata
import collections
import collections.abc
import trueskill
import sys

def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
        d[k] = update(d.get(k, {}), v)
    else:
        d[k] = v
  return d

def skill(game):
    f = open('./out/'+game+'/alltournaments.json')
    alltournaments = json.load(f)

    allmatches = []
    alreadyAddedTournaments = []

    f = open('./out/'+game+'/allplayers.json')
    allplayers = json.load(f)

    f = open('./out/'+game+'/allleagues.json')
    allleagues = json.load(f)

    allAllTournaments = []

    leaguesRegionalToNational = sorted(
        list(alltournaments.keys()),
        key=lambda x: 1 if allleagues[x].get("state") == None else 0
    )

    for league in leaguesRegionalToNational:
        #if allleagues[league].get("region") != "SA":
        #    continue

        for tournament in alltournaments[league].values():
            if "link" in tournament:
                if tournament["link"] in alreadyAddedTournaments and tournament["link"] is not None:
                    continue
            
            tournament["league"] = league

            regional = True if allleagues[league].get("state") else False
            wifi = True if allleagues[league].get("wifi") else False
            huge = True if tournament.get("player_number") >= 64 else False
            
            if tournament.get("player_number") < 8:
                continue

            tournament["regional"] = regional
            tournament["wifi"] = wifi
            tournament["huge"] = huge

            allAllTournaments.append(tournament)
            
            if "link" in tournament:
                alreadyAddedTournaments.append(tournament["link"])
    
    print("Tournaments: "+str(len(allAllTournaments)))

    allAllTournaments = sorted(allAllTournaments, key=lambda t: t["time"])

    for tournament in allAllTournaments:
        linkage = tournament["linkage"]

        for match in tournament["matches"]:
            myMatch = {}

            if -1 in match["participants"].values():
                continue

            p1 = next((p for p in linkage if linkage[p] == list(match["participants"].keys())[0]), None)
            p2 = next((p for p in linkage if linkage[p] == list(match["participants"].keys())[1]), None)

            if p1 == None or p2 == None:
                continue

            p1apid = allplayers["mapping"].get(tournament["league"]+":"+p1)
            p2apid = allplayers["mapping"].get(tournament["league"]+":"+p2)

            if p1apid == None or p2apid == None:
                continue
        
            wifi = False
            if tournament["wifi"]:
                wifi = True
            
            local = False
            if tournament["regional"]:
                local = True
            
            huge = False
            if tournament["huge"]:
                huge = True

            # p1 wins
            for i in range(list(match["participants"].values())[0]):
                myMatch = [p1apid, p2apid, wifi, local, huge]
                allmatches.append(myMatch)

            # p2 wins
            for i in range(list(match["participants"].values())[1]):
                myMatch = [p2apid, p1apid, wifi, local, huge]
                allmatches.append(myMatch)
    
    print("Matches: "+str(len(allmatches)))
    print("Players: "+str(len(allplayers["players"])))

    players = {}

    mySigma = trueskill.SIGMA

    ts = trueskill.TrueSkill(
        draw_probability=0,
        mu=mySigma*3,
        sigma=mySigma/2,
        beta=mySigma/1,
        tau=mySigma/100
    )
    ts.make_as_global()

    #mySigma = trueskill.SIGMA*4

    tsHuge = trueskill.TrueSkill(
        draw_probability=0,
        mu=mySigma*3,
        sigma=mySigma/2,
        beta=mySigma/1,
        tau=mySigma/1000
    )

    #mySigma = trueskill.SIGMA/1.2

    tsOnline = trueskill.TrueSkill(
        draw_probability=0,
        mu=mySigma*3,
        sigma=mySigma/2,
        beta=mySigma/2,
        tau=mySigma/75
    )

    #mySigma = trueskill.SIGMA/8

    tsLocal = trueskill.TrueSkill(
        draw_probability=0,
        mu=mySigma*3,
        sigma=mySigma/2,
        beta=mySigma/8,
        tau=mySigma/10
    )

    for player in allplayers["players"]:
        if player.get("apid", None) != None:
            players[player["apid"]] = {}
            players[player["apid"]]["player"] = player
            players[player["apid"]]["rating"] = trueskill.Rating()

    for i, match in enumerate(allmatches):
        if players.get(match[0]) and players.get(match[1]):
            theTs = ts

            if match[2]:
                theTs = tsOnline

            if match[3]:
                theTs = tsLocal
            
            if match[4]:
                theTs = tsHuge

            new_p1, new_p2 = trueskill.rate_1vs1(players[match[0]]["rating"], players[match[1]]["rating"], env=theTs)
            players[match[0]]["rating"] = new_p1
            players[match[1]]["rating"] = new_p2

            print("Matches..."+str(i)+"/"+str(len(allmatches))+"..."+str(i/len(allmatches)*100)+"%", end="\r")

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
    
    higherScore = max(ranking[0]["ts"], 1)
    subdivisions = 20

    with open('./out/'+game+'/leaderboard.json', 'w') as outfile:
        json.dump(ranking, outfile, indent=4, sort_keys=True)

    with open('./out/'+game+'/leaderboardreadable.txt', 'w') as outfile:
        for i, p in enumerate(ranking):
            outfile.write(
                str(i+1) + "\t\t" + 
                chr(ord('A')+int((1-(p["ts"]/higherScore))*subdivisions)) + "\t" +
                (p.get("org")+" " if p.get("org") not in [None, "null", " "] else "") +
                p["name"] +
                " ("+p.get("country_code")+")" +
                " ("+(p.get("mains")[0] if len(p.get("mains"))>0 else "?")+")" +
                "\t\t\t\t\t\t" + str(p["ts"]) + "\n")
    
    for country in ["BR", "AR", "BO", "CL", "EC", "UY", "PE", "CO"]:
        with open('./out/'+game+'/leaderboardreadable_'+country+'.txt', 'w') as outfile:
            for i, p in enumerate(ranking):
                if p.get("country_code") != country: continue

                outfile.write(
                    str(i+1) + "\t\t" + 
                    chr(ord('A')+int((1-(p["ts"]/higherScore))*subdivisions)) + "\t" +
                    (p.get("org")+" " if p.get("org") not in [None, "null", " "] else "") +
                    p["name"] +
                    " ("+p.get("country_code")+")" +
                    " ("+(p.get("mains")[0] if len(p.get("mains"))>0 else "?")+")" +
                    "\t\t\t\t\t\t" + str(p["ts"]) + "\n")

    with open('./out/'+game+'/allplayers.json', 'w') as outfile:
        json.dump(allplayers, outfile, indent=4, sort_keys=True)

    with open('./out/'+game+'/ts_env.json', 'w') as outfile:
        json.dump({
            "mu": ts.mu,
            "sigma": ts.sigma,
            "beta": ts.beta
        }, outfile, indent=4)

if __name__ == "__main__":
	games = os.listdir("./games")

	if len(sys.argv) >= 2:
		game = sys.argv[1]
		skill(game)
	else:
		for game in games:
			skill(game)