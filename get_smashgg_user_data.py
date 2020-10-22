import time
import datetime
import requests
import json
import pprint
import datetime
import os

SMASHGG_KEY = os.environ.get("SMASHGG_KEY")

f = open('alltournaments.json')
alltournaments = json.load(f)

f = open('allplayers.json')
allplayers = json.load(f)

for league in alltournaments:
    for tournament in alltournaments[league].values():
        if not tournament["link"]:
          continue

        tournament_slug_start = tournament["link"].index("tournament/")
        slug = tournament["link"][tournament_slug_start:]

        print(slug)

        r = requests.post(
          'https://api.smash.gg/gql/alpha',
          headers={
            'Authorization': 'Bearer'+SMASHGG_KEY,
          },
          json={
            'query': '''
            query evento($eventSlug: String!) {
              event(slug: $eventSlug) {
                entrants {
                  nodes{
                    name
                    participants {
                      user {
                        id
                        slug
                        name
                        authorizations(types: [TWITTER]) {
                          externalUsername
                        }
                        player {
                          gamerTag
                          prefix
                        }
                        location {
                          city
                          state
                        }
                        images(type: "profile") {
                          url
                        }
                      }
                    }
                  }
                }
              }
            },
          ''',
            'variables': {
              "eventSlug": slug
            },
          }
        )

        resp = json.loads(r.text)

        print(resp)

        if resp is None or resp.get("data") is None or resp.get("data").get("event") is None:
          continue

        data_entrants = resp["data"]["event"]["entrants"]["nodes"]

        for gg_entrant in data_entrants:
          for braacket_entrant in tournament["ranking"].values():
            if braacket_entrant["tournament_name"] is None:
              continue
            if gg_entrant["name"] == braacket_entrant["tournament_name"]:
              player_id = allplayers["mapping"].get(league+":"+braacket_entrant["uuid"])

              if player_id is None:
                print("Not found: "+str(braacket_entrant))
                continue

              player_obj = allplayers["players"][player_id]

              if gg_entrant["participants"][0]["user"] is None:
                continue

              player_obj["smashgg_id"] = gg_entrant["participants"][0]["user"]["id"]
              player_obj["smashgg_slug"] = gg_entrant["participants"][0]["user"]["slug"]
              player_obj["full_name"] = gg_entrant["participants"][0]["user"]["name"]

              if gg_entrant["participants"][0]["user"]["authorizations"] is not None:
                player_obj["twitter"] = "https://twitter.com/"+gg_entrant["participants"][0]["user"]["authorizations"][0]["externalUsername"]

              if gg_entrant["participants"][0]["user"]["images"] is not None:
                if len(gg_entrant["participants"][0]["user"]["images"]) > 0:
                  player_obj["smashgg_image"] = gg_entrant["participants"][0]["user"]["images"][0]["url"]

              break

        time.sleep(1)

with open('allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)