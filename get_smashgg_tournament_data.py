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

def get_smashgg_tournament_info(tournament, currentKey):
	global SMASHGG_KEYS

	# not on smashgg, skip
	if not tournament["link"]:
		print("Not on smashgg, skipping")
		return
	
	tournament_slug_start = tournament["link"].index("tournament/")
	slug = tournament["link"][tournament_slug_start:]

	if tournament["ranking"] is None:
		return

	page = 1

	while True:
		r = requests.post(
			'https://api.smash.gg/gql/alpha',
			headers={
				'Authorization': 'Bearer'+SMASHGG_KEYS[currentKey],
			},
			json={
				'query': '''
				query evento($eventSlug: String!) {
					event(slug: $eventSlug) {
						entrants(query: {page: '''+str(page)+''', perPage: 120}) {
							nodes{
								name
								participants {
									user {
										id
									}
								}
							}
							pageInfo{
								totalPages
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
		time.sleep(1)

		resp = json.loads(r.text)

		if resp is None or \
		resp.get("data") is None or \
		resp["data"].get("event") is None or \
		resp["data"]["event"].get("entrants") is None:
			print(resp)
			break

		data_entrants = resp["data"]["event"]["entrants"]["nodes"]

		if data_entrants is None or len(data_entrants) == 0:
			break
	
		num_pages = resp["data"]["event"]["entrants"]["pageInfo"]["totalPages"]

		print("Page: "+str(page)+"/"+str(num_pages)+
			"\tEntries: "+str(len(data_entrants)))

		for gg_entrant in data_entrants:
			for braacket_entrant in tournament["ranking"].items():
				if braacket_entrant[1]["tournament_name"] is None:
					continue
				if gg_entrant["name"] == braacket_entrant[1]["tournament_name"]:
					if gg_entrant["participants"][0]["user"] is None:
						# no smashgg data, nothing to do here
						continue
				
					braacket_entrant[1]["smashgg_id"] = gg_entrant["participants"][0]["user"]["id"]

		if page >= num_pages:
			break

		page += 1