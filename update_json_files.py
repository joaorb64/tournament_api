import requests

url = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json'

r = requests.get(url, allow_redirects=True)
open('countries+states+cities.json', 'wb').write(r.content)