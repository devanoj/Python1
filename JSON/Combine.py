import json

# Open each file and load the data
with open('dogs1.json', 'r') as f1, open('dogs2.json', 'r') as f2, open('dogs3.json', 'r') as f3, open('dogs4.json', 'r') as f4, open('dogs5.json', 'r') as f5:
    data1 = json.load(f1)
    data2 = json.load(f2)
    data3 = json.load(f3)
    data4 = json.load(f4)
    data5 = json.load(f5)

# Combine the data from all the files
combined_data = data1 + data2 + data3 + data4 + data5

# Write the combined data to a new file
with open('combined.json', 'w') as outfile:
    json.dump(combined_data, outfile)