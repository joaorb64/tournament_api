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

    weekResults = []

    currentKey = 0

    f = open('./games/'+game+'/config.json')
    config = json.load(f)

    f = open('./games/'+game+'/next_tournaments_countries.json')
    countries = json.load(f)

    f = open('./out/'+game+'/smashgg_cache.json')
    smashgg_cache = json.load(f)
    
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
    
    total = len(weekTournaments)
    i = 1

    for tournament in weekTournaments.values():
        print(str(i)+"/"+str(total), end="\r")
        i+=1

        if not tournament.get("lat") and not tournament.get("lng") and not tournament.get("country_code"):
            continue

        if tournament.get("provider") != "challonge":
            r = requests.post(
                'https://api.smash.gg/gql/alpha',
                headers={
                    'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
                },
                json={
                    'query': '''
                    query PlayerSetsInEvent($eventId: ID!) {
                        event(id: $eventId) {
                            state
                            type
                            numEntrants
                            standings(query: {page: 1, perPage: 1}){
                                nodes {
                                    placement
                                    entrant {
                                        id
                                        name
                                        participants {
                                            user {
                                                id
                                            }
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
            time.sleep(1/len(SMASHGG_KEYS))
            currentKey = (currentKey+1)%len(SMASHGG_KEYS)

            if resp == None or resp.get("data") == None or resp.get("data").get("event") == None:
                continue
        
            numEntrants = resp.get("data", {}).get("event", {}).get("numEntrants")

            if not numEntrants or numEntrants < 6:
                continue

            if resp.get("data", {}).get("event", {}).get("state") == "COMPLETED" \
                and resp.get("data").get("event").get("type") == 1:
                winner = resp.get("data").get("event").get("standings").get("nodes")[0]
                entrantId = winner.get("entrant").get("id")

                participant = winner.get("entrant", {}).get("participants", [{}])[0].get("user", {})

                if participant is not None:
                    userId = participant.get("id")

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
                char_data = resp.get("data")
                time.sleep(1/len(SMASHGG_KEYS))
                currentKey = (currentKey+1)%len(SMASHGG_KEYS)

                if char_data:
                    char_data = char_data.get("event").get("sets").get("nodes")
                else:
                    print("Error fetching character data? -- cancel")

                char_usage = {}

                # Char usage
                for _game in char_data:
                    if _game.get("games"):
                        for selection in _game.get("games"):
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
                    char_in_json = next((c for c in smashgg_characters["entities"]["character"] if c["id"] == char[0]), None)

                    if char_in_json:
                        char_usage_named[charname_to_braacket.get(char_in_json["name"])] = char[1]
                
                if len(char_usage_named.keys()) == 0:
                    if userId is not None and str(userId) in smashgg_cache:
                        char_usage_named = smashgg_cache[str(userId)].get("character_usage")
                
                character = None

                if len(char_usage_named.keys()) > 0:
                    character = sorted(char_usage_named.items(), key = lambda t: t[1])[-1][0]

                if tournament.get("lat") == None or tournament.get("lng") == None:
                    if tournament.get("country_code"):
                        country = next((c for c in countries_json if c["iso2"] == tournament.get("country_code")), None)
                        if country:
                            tournament["lat"] = country["latitude"]
                            tournament["lng"] = country["longitude"]

                weekResults.append({
                    "winner": winner.get("entrant").get("name"),
                    "character": character,
                    "lat": tournament.get("lat"),
                    "lng": tournament.get("lng"),
                    "country_code": tournament.get("country_code"),
                    "isOnline": tournament.get("isOnline"),
                    "numEntrants": numEntrants,
                    "url": tournament.get("url"),
                    "name": tournament.get("name"),
                    "tournament": tournament.get("tournament"),
                    "tournament_multievent": tournament.get("tournament_multievent")
                })
        else:
            print("TODO: ADD CHALLONGE HERE")
        
    with open('./out/'+game+'/week_tournament_results.json', 'w') as outfile:
        json.dump(weekResults, outfile, indent=4)
    
    print()
    print("OK")

if __name__ == "__main__":
    games = os.listdir("./games")

    if len(sys.argv) >= 2:
        game = sys.argv[1]
        gen_week_results(game)
    else:
        for game in games:
            gen_week_results(game)
            time.sleep(1)