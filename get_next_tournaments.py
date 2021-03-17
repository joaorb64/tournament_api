import time
import datetime
import requests
import json
import pprint
import datetime
import os
from collections import Counter
import sys

if os.path.exists("auth.json"):
  f = open('auth.json')
  auth_json = json.load(f)
  SMASHGG_KEYS = auth_json["SMASHGG_KEYS"]
else:
  SMASHGG_KEYS = os.environ.get("SMASHGG_KEYS")

def get_next_tournaments(game):
    currentKey = 0

    f = open('./games/'+game+'/config.json')
    config = json.load(f)

    f = open('./games/'+game+'/next_tournaments_countries.json')
    countries = json.load(f)
    
    oldTournaments = {}

    try:
        f = open('./out/'+game+'/nexttournaments.json')
        oldTournaments = json.load(f)
    except Exception as e:
        print("No previous tournaments file")

    for country in countries:

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
                    query TournamentsByCountry($cCode: String!, $perPage: Int!) {
                        tournaments(query: {
                        perPage: $perPage
                        page: '''+str(page)+'''
                        filter: {
                            countryCode: $cCode
                            videogameIds: ['''+str(config["smashgg_videogame_id"])+''']
                            upcoming: true
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
                    "cCode": country,
                    "perPage": 20
                    },
                }
            )
            time.sleep(1/len(SMASHGG_KEYS))
            currentKey = (currentKey+1)%len(SMASHGG_KEYS)

            resp = json.loads(r.text)

            if resp is None or \
            resp.get("data") is None or \
            resp["data"].get("tournaments") is None or \
            resp["data"]["tournaments"].get("nodes") is None:
                print(country+" "+str(resp))
                break
        
            data = resp["data"]["tournaments"]["nodes"]

            if data == None or len(data) == 0:
                break

            print(country+" - Page: "+str(page)+"\tTournaments: "+str(len(data)))

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
                            events {
                            id
                            name
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
                tournament_data = resp["data"]["tournament"]

                smash_ultimate_tournaments = 0

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
                        event["url"] = "https://smash.gg"+tournament_data["url"]
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
                    
                    tournaments.append(event)

            page+=1
        
        countries[country]["events"] = tournaments
    
    for oldTournament in oldTournaments:
        if time.time() <= oldTournament["tournament_endAt"]:
            tournaments.append(oldTournament)

    with open('./out/'+game+'/nexttournaments.json', 'w') as outfile:
        json.dump(countries, outfile, indent=4)

if __name__ == "__main__":
    games = os.listdir("./games")

    if len(sys.argv) >= 2:
        game = sys.argv[1]
        get_next_tournaments(game)
    else:
        for game in games:
            get_next_tournaments(game)
            time.sleep(1)