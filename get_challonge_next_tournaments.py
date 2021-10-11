from sys import path
from typing import Text
from bs4 import BeautifulSoup
import json
import re
import unicodedata
import shutil
import os
import requests
import datetime
import locale
from dateutil import parser

if os.path.exists("auth.json"):
  f = open('auth.json')
  auth_json = json.load(f)
  CHALLONGE_KEY = auth_json["CHALLONGE_KEY"]
else:
  CHALLONGE_KEY = os.environ.get("CHALLONGE_KEY")

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

f = open('./countries+states+cities.json')
countries_json = json.load(f)

def get_tournaments(gameId, gameName):
    result = []

    r = requests.get(
        f"http://challonge.com/search/events.json?q=&&page=1&&per=200&&filters[name]=&&filters[state]=registering&&filters[game_ids]={gameId}",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
    )

    events = json.loads(r.text)

    for event in events.get("collection"):
        url = f'http://challonge.com/{event.get("link")}'

        r = requests.get(
            url,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
            }
        )
        soup = BeautifulSoup(r.text, features="lxml")

        div = soup.find('div', {"data-editable": "false"})

        data = json.loads(div["data-event"])

        countryCode = ""
        stateName = ""
        stateCode = None
        lat = None
        lng = None

        if data.get("location"):
            if len(data.get("location").split(",")) < 3:
                continue
            countryCode = data.get("location").split(",")[-1].strip()
            stateName = data.get("location").split(",")[-2].strip()
        
        countryObj = next((c for c in countries_json if c.get("iso2") == countryCode), None)
        
        if not countryObj:
            continue

        state = next((s for s in countryObj.get("states") if s.get("name") == stateName), None)

        if state:
            stateCode = state.get("state_code")
            lat = float(state.get("latitude"))
            lng = float(state.get("longitude"))

        tournament = next((t for t in data.get("tournaments", []) if t.get("game_name") == gameName), None)

        if tournament:
            r = requests.get(
                f'https://joao_shino:{CHALLONGE_KEY}@api.challonge.com/v1/tournaments/{data.get("id")}.json?include_participants=1',
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
                }
            )
            
            tournament_data = json.loads(r.text)

            if not tournament_data.get("tournament"):
                continue

            if data.get("startsAt")[-12] == " ":
                data["startsAt"] = data.get("startsAt")[:-12]+'0'+\
                                        data.get("startsAt")[-11:]

            normalized = {
                "id": "chal"+str(data.get("id")),
                "name": tournament.get("name"),
                "numEntrants": tournament_data.get("tournament").get("participants_count"),
                "startAt": parser.parse(data.get("startsAt")).timestamp(),
                "tournament": data.get("title"),
                "url": tournament.get("full_challonge_url"),
                "tournament_startAt": parser.parse(data.get("startsAt")).timestamp(),
                "tournament_endAt": parser.parse(data.get("startsAt")).timestamp(),
                "tournament_registrationClosesAt": parser.parse(data.get("startsAt")).timestamp(),
                "images": [
                    {
                        "url": data.get("logoUrl")[2:],
                        "type": "profile"
                    },
                    {
                        "url": data.get("bannerUrl")[2:],
                        "type": "banner"
                    }
                ],
                "tournament_multievent": True,
                "tournament_venueAddress": data.get("location"),
                "tournament_addrState": stateCode,
                "country_code": countryCode,
                "lat": lat,
                "lng": lng,
                "provider": "challonge"
            }
            
            result.append(normalized)
    
    print(f"Tournaments in challonge: {len(result)}")

    return result