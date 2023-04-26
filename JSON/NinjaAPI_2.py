import requests
import json

name = '5'
api_url = 'https://api.api-ninjas.com/v1/dogs?barking={}'.format(name)

response = requests.get(api_url, headers={'X-Api-Key': 'BI+Alyvlya8ICTKjNAny1w==zTNZj4XYZz6ESIVw'})
if response.status_code == requests.codes.ok:
    # Parse the response JSON data
    data = json.loads(response.text)

    # Write the JSON data to a file
    with open('dogs5.json', 'w') as outfile:
        json.dump(data, outfile)
else:
    print("Error:", response.status_code, response.text)