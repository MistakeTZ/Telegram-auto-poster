import json

with open("output.txt") as file:
    valid_json = file.read().replace("\\n", "")
    array = json.loads(valid_json)

for item in array:
    print(item)
