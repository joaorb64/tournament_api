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

f = open('./smashgg_countrycodes.json')
smashgg_countrycodes = json.load(f)

f = open('./countries+states+cities.json')
countries_json = json.load(f)

def gen_week_results(game):
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
    
    f = open('./games/'+game+'/charnames_smashgg_to_braacket.json')
    charname_to_braacket = json.load(f)

    smashgg_characters = json.loads(requests.get("https://api.smash.gg/characters").text)
    
    for tournament in weekTournaments.values():
        if tournament["state"] == "COMPLETED":
            r = requests.post(
                'https://api.smash.gg/gql/alpha',
                headers={
                    'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
                },
                json={
                    'query': '''
                    query PlayerSetsInEvent($eventId: ID!) {
                        event(id: $eventId) {
                            standings(query: {page: 1, perPage: 1}){
                                nodes {
                                    placement
                                    entrant {
                                        id
                                    }
                                }
                            }
                        }
                    },
                    ''',
                    'variables': {
                    "eventId": tournament["id"]
                    },
                }
            )
            resp = json.loads(r.text)
            time.sleep(1/len(SMASHGG_KEYS))
            currentKey = (currentKey+1)%len(SMASHGG_KEYS)

            winner = resp.get("data").get("event").get("standings").get("nodes")[0]
            entrantId = winner.get("entrant").get("id")

            r = requests.post(
                'https://api.smash.gg/gql/alpha',
                headers={
                    'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
                },
                json={
                    'query': '''
                    query PlayerSetsInEvent($eventId: ID!) {
                        event(id: $eventId) {
                            sets(
                                page: 1,
                                perPage: 200,
                                filters: {entrantIds: ''' + str(entrantId) + '''},
                            ) {
                                nodes {
                                    displayScore
                                    games {
                                        selections {
                                            entrant {
                                                id
                                            }
                                            selectionValue
                                        }
                                    }
                                }
                            }
                        }
                    },
                    ''',
                    'variables': {
                    "eventId": tournament["id"]
                    },
                }
            )
            resp = json.loads(r.text)
            print(resp)
            char_data = resp.get("data")
            print(char_data)
            time.sleep(1/len(SMASHGG_KEYS))
            currentKey = (currentKey+1)%len(SMASHGG_KEYS)

            if char_data:
                char_data = char_data.get("event").get("sets").get("nodes")
            else:
                print("Error fetching character data? -- cancel")
                continue

            char_usage = {}

            # Char usage
            for game in char_data:
                if game.get("games"):
                    for selection in game.get("games"):
                        if selection.get("selections"):
                            for selection_entry in selection.get("selections"):
                                if selection_entry["entrant"]["id"] == entrantId:
                                    if selection_entry["selectionValue"] not in char_usage.keys():
                                        char_usage[selection_entry["selectionValue"]] = 1
                                    else:
                                        char_usage[selection_entry["selectionValue"]] += 1
            
            char_usage = {k: v for k, v in sorted(char_usage.items(), key=lambda item: item[1], reverse=True)}

            char_usage_named = {}
            char_in_json = None

            for char in char_usage.items():
                char_in_json = next((c for c in smashgg_characters["character"] if c["id"] == char[0]), None)

            if char_in_json:
                char_usage_named[char_in_json["name"]] = {}
                char_usage_named[char_in_json["name"]]["name"] = char_in_json["name"]
                char_usage_named[char_in_json["name"]]["usage"] = char[1]
                char_usage_named[char_in_json["name"]]["icon"] = char_in_json.get("images")[1].get("url")
            
            print(char_usage_named)

if __name__ == "__main__":
    games = os.listdir("./games")

    if len(sys.argv) >= 2:
        game = sys.argv[1]
        gen_week_results(game)
    else:
        for game in games:
            gen_week_results(game)
            time.sleep(1)