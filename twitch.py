import requests
import json
import datetime
import os

if os.path.exists("auth.json"):
  f = open('auth.json')
  auth_json = json.load(f)
  TWITCH_CLIENT_ID = auth_json["TWITCH_CLIENT_ID"]
  TWITCH_CLIENT_SECRET = auth_json["TWITCH_CLIENT_SECRET"]
else:
  TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
  TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")

r = requests.post('https://id.twitch.tv/oauth2/token?client_id='+TWITCH_CLIENT_ID+'&client_secret='+TWITCH_CLIENT_SECRET+'&grant_type=client_credentials')
resp = json.loads(r.text)

token = resp.get("access_token", None)

r = requests.get(
    "https://api.twitch.tv/helix/games?name=Super Smash Bros. Ultimate",
    headers={
        'Authorization': 'Bearer '+token,
        'Client-Id': 'rwixu6mzg5ziu2d1xi22rws67dk0lh'
    }
)
resp = json.loads(r.text)
print(resp)

clips = {}

for j in range(7):
    print(str(j) + " days back")
    startTime = (datetime.datetime.utcnow()-datetime.timedelta(days=(j+2))).isoformat("T") + "Z"
    endTime = (datetime.datetime.utcnow()-datetime.timedelta(days=(j+1))).isoformat("T") + "Z"

    print(startTime)
    print(endTime)

    pagination = ""

    for i in range(100):
        r = requests.get(
            "https://api.twitch.tv/helix/clips?game_id=504461&started_at="+startTime+"&ended_at="+endTime+"&first=100&after="+pagination,
            headers={
                'Authorization': 'Bearer '+token,
                'Client-Id': 'rwixu6mzg5ziu2d1xi22rws67dk0lh'
            }
        )
        resp = json.loads(r.text)
        pagination = resp["pagination"].get("cursor", None)

        for c in resp["data"]:
            if c["language"] not in clips:
                clips[c["language"]] = []
            clips[c["language"]].append(c)
        
        print(i, end="\r")
        
        if pagination == None:
            break

with open('out/twitchclips.json', 'w') as outfile:
	json.dump(clips, outfile, indent=4, sort_keys=True)