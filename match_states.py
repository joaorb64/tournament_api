import json
import os
import unicodedata

def remove_accents_lower(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

f = open('out/allplayers.json')
allplayers = json.load(f)

f = open('cities.json')
cities = json.load(f)

f = open('countries.json')
countries = json.load(f)

for player in allplayers["players"]:
  if "country" in player.keys() and player["country"] is not None:
    country = next(
      (c for c in countries if remove_accents_lower(c["name"]) == remove_accents_lower(player["country"])),
      None
    )

    if country is not None:
      player["country_code"] = country["iso2"]

      if "city" in player.keys() and player["city"] is not None:
        city = next(
          (c for c in cities if remove_accents_lower(c["name"]) == remove_accents_lower(player["city"])
          and c["country_code"] == player["country_code"]),
          None
        )

        if city is not None:
          player["state"] = city["state_code"]


with open('out/allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)