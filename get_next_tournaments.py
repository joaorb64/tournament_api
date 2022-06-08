import time
import datetime
from typing import List
import requests
import json
import pprint
import datetime
import os
from collections import Counter
import sys
from get_challonge_next_tournaments import get_tournaments

if os.path.exists("auth.json"):
  f = open('auth.json')
  auth_json = json.load(f)
  SMASHGG_KEYS = auth_json["SMASHGG_KEYS"]
else:
  SMASHGG_KEYS = os.environ.get("SMASHGG_KEYS")

f = open('./smashgg_countrycodes.json')
smashgg_countrycodes = json.load(f)

f = open('./countries+states+cities.json')
countries_json = json.load(f)

def get_next_tournaments(game):
    print(game)

    currentKey = 0

    f = open('./games/'+game+'/config.json')
    config = json.load(f)

    f = open('./games/'+game+'/next_tournaments_countries.json')
    countries = json.load(f)
    
    oldTournaments = {}
    updateTime = 0

    try:
        f = open('./out/'+game+'/nexttournaments.json')
        oldTournaments = json.load(f)
        updateTime = oldTournaments.get("updateTime", 0)
    except Exception as e:
        print("No previous tournaments file")

    weekTournaments = {}
    try:
        f = open('./out/'+game+'/week_tournaments.json')
        weekTournaments = json.load(f)
    except Exception as e:
        print("No previous week tournaments file")

    page = 1

    tournaments = []

    while True:
        r = requests.post(
            'https://api.smash.gg/gql/alpha',
            headers={
                'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
            },
            json={
                'query': '''
                query Tournaments($perPage: Int!) {
                    tournaments(query: {
                        perPage: $perPage
                        page: '''+str(page)+'''
                        filter: {
                            videogameIds: ['''+str(config["smashgg_videogame_id"])+'''],
                            upcoming: true,
                            computedUpdatedAt: '''+str(int(updateTime-datetime.timedelta(hours=1).total_seconds()))+'''
                        }
                    }) {
                    nodes {
                        id
                        startAt
                        events {
                            id
                            videogame {
                                id
                            }
                            startAt
                            }
                        }
                    }
                },
                ''',
                'variables': {
                    "perPage": 20
                },
            }
        )
        time.sleep(4/len(SMASHGG_KEYS))
        currentKey = (currentKey+1)%len(SMASHGG_KEYS)

        resp = json.loads(r.text)

        if resp is None or \
        resp.get("data") is None or \
        resp["data"].get("tournaments") is None or \
        resp["data"]["tournaments"].get("nodes") is None:
            print(str(resp))
            break
    
        data = resp["data"]["tournaments"]["nodes"]

        if data == None or len(data) == 0:
            break

        print("Page: "+str(page)+"\tTournaments: "+str(len(data)))

        for tournament in data:
            r = requests.post(
                'https://api.smash.gg/gql/alpha',
                headers={
                'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
                },
                json={
                'query': '''
                    query Tournament($tournamentId: ID!) {
                        tournament(id: $tournamentId) {
                            id
                            name
                            url
                            city
                            timezone
                            startAt
                            endAt
                            registrationClosesAt
                            venueName
                            venueAddress
                            addrState
                            lat
                            lng
                            events {
                                id
                                name
                                slug
                                isOnline
                                state
                                numEntrants
                                videogame {
                                    id
                                }
                                startAt
                                phaseGroups {
                                    id
                                    phase {
                                        id
                                        name
                                    }
                                    progressionsOut {
                                        id
                                    }
                                }
                            }
                            streams {
                                streamName
                            }
                            images{
                                id
                                url
                                type
                            }
                            countryCode
                        }
                    },
                ''',
                'variables': {
                    "tournamentId": tournament["id"]
                },
                }
            )
            time.sleep(1/len(SMASHGG_KEYS))
            currentKey = (currentKey+1)%len(SMASHGG_KEYS)

            resp = json.loads(r.text)
            tournament_data = resp.get("data", {}).get("tournament")

            smash_ultimate_tournaments = 0

            if tournament_data == None or tournament_data["events"] == None:
                continue

            for event in tournament_data["events"]:
                if event["videogame"]["id"] == config["smashgg_videogame_id"]:
                    smash_ultimate_tournaments += 1

            for event in tournament_data["events"]:
                # Smash Ultimate
                if event["videogame"]["id"] != config["smashgg_videogame_id"]:
                    continue

                if event["startAt"] > time.time():
                    event["tournament"] = tournament_data["name"]
                    event["tournament_id"] = tournament_data["id"]
                    event["city"] = tournament_data["city"]
                    event["url"] = "https://smash.gg"+"/"+event["slug"]
                    event["streams"] = tournament_data["streams"]
                    event["timezone"] = tournament_data["timezone"]
                    event["tournament_startAt"] = tournament_data["startAt"]
                    event["tournament_endAt"] = tournament_data["endAt"]
                    event["tournament_registrationClosesAt"] = tournament_data["registrationClosesAt"]
                    event["images"] = tournament_data["images"]
                    event["tournament_multievent"] = False if smash_ultimate_tournaments <= 1 else True
                    event["tournament_venueName"] = tournament_data["venueName"]
                    event["tournament_venueAddress"] = tournament_data["venueAddress"]
                    event["tournament_addrState"] = tournament_data["addrState"]
                    event["country_code"] = tournament_data["countryCode"]
                    event["lat"] = tournament_data["lat"]
                    event["lng"] = tournament_data["lng"]

                    r = requests.get("https://api.smash.gg"+tournament_data["url"])
                    oldApiData = json.loads(r.text)

                    attendeeRequirements = \
                        oldApiData.get("entities", {})\
                        .get("tournament", {})\
                        .get("attendeeRequirements", {})
                    
                    countryRequirements = None
                    if attendeeRequirements != None and not isinstance(attendeeRequirements, list):
                        countryRequirements = attendeeRequirements.get("country", None)

                    if countryRequirements:
                        regionLock = []
                        for country in countryRequirements:
                            name = next((c["country"] for c in smashgg_countrycodes if c["id"] == country), None)
                            if name:
                                ccode = next((c["iso2"] for c in countries_json if c["name"]==name or c["native"]==name), None)
                                if ccode:
                                    name = ccode
                                codemap = {
                                    "Croatia": "HR",
                                    "Netherlands": "NL",
                                    "England": "GB",
                                    "Wales": "GB",
                                    "Scotland": "GB",
                                    "Åland Islands": "AX",
                                    "United States Virgin Islands": "VI",
                                    "Vatican City": "VA",
                                    "Saint Vincent and the Grenadines": "VC",
                                    "Trinidad and Tobago": "TT",
                                    "Turks and Caicos Islands": "TC",
                                    "Sint Maarten": "SX",
                                    "Antigua and Barbuda": "AG",
                                    "Bonaire": "BQ",
                                    "Bahamas": "BS",
                                    "Saint Kitts and Nevis": "KN",
                                    "Saint Martin": "MF",
                                    "British Virgin Islands": "VG",
                                    "South Korea": "KR",
                                    "Hong Kong": "HK"
                                }
                                if name in codemap:
                                    name = codemap[name]
                                
                                regionLock.append(name)
                        event["region_lock"] = regionLock
                        print(regionLock)
                
                tournaments.append(event)
        page+=1
    
    # Challonge
    try:
        if config.get("challonge_videogame_id") and config.get("challonge_game_name"):
            print("Challonge")
            tournaments.extend(get_tournaments(config["challonge_videogame_id"], config["challonge_game_name"]))
    except Exception as e:
        print("Challonge error: "+str(e))

    print("Tournament number: "+str(len(tournaments)))
    
    for oldTournament in oldTournaments.get("events", []):
        if "tournament_endAt" in oldTournament and "id" in oldTournament:
            found = next((t for t in tournaments if t.get("id", None) == oldTournament["id"]), None)

            if not found and time.time() <= oldTournament["tournament_endAt"]:
                tournaments.append(oldTournament)
    
    for tournament in tournaments:
        weekTournaments[str(tournament["id"])] = tournament

    # remove tournaments past last week
    for tournament in list(weekTournaments.items()):
        if tournament[1]["startAt"] + datetime.timedelta(days=7) > time.mktime(datetime.date.today().timetuple()):
            weekTournaments.pop(tournament[0])

    with open('./out/'+game+'/nexttournaments.json', 'w') as outfile:
        json.dump(
            {"updateTime": int(time.time()), "events": tournaments},
            outfile,
            indent=4
        )
    
    with open('./out/'+game+'/week_tournaments.json', 'w') as outfile:
        json.dump(weekTournaments, outfile, indent=4)

if __name__ == "__main__":
    games = os.listdir("./games")

    if len(sys.argv) >= 2:
        game = sys.argv[1]
        get_next_tournaments(game)
    else:
        for game in games:
            get_next_tournaments(game)
            time.sleep(1)