import json
import os
import unicodedata

def remove_accents_lower(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

f = open('allplayers.json')
allplayers = json.load(f)

f2 = open('municipios.json')
municipios = json.load(f2)

f3 = open('estados.json')
estados = json.load(f3)

for player in allplayers["players"]:
    if "state" not in player.keys() or player["state"] is None or player["state"] == "":
        if "city" in player.keys() and player["city"] is not None:
            municipio = next(
                (m for m in municipios if remove_accents_lower(m["nome"]) == remove_accents_lower(player["city"])),
                None
            )

            if municipio is not None:
                estado = next(
                    (e for e in estados if e["codigo_uf"] == municipio["codigo_uf"]),
                    None
                )

                if estado is not None:
                    player["state"] = estado["uf"]
                    print(estado["uf"])


with open('allplayers.json', 'w') as outfile:
  json.dump(allplayers, outfile, indent=4, sort_keys=True)