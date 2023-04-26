import pandas as pd
import json

with open('combined.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

cols_to_drop = ['min_life_expectancy', 'max_life_expectancy', 'max_height_male',
                'max_height_female', 'max_weight_male', 'max_weight_female',
                'min_height_male', 'min_height_female', 'min_weight_male',
                'min_weight_female', 'grooming', 'drooling', 'good_with_strangers', 
                'playfulness', 'protectiveness', 'energy', "image_link"]

df.drop(columns=cols_to_drop, inplace=True)

result = df.to_json(orient='records')

with open('output.json', 'w') as f:
    json.dump(json.loads(result), f, indent=4)
