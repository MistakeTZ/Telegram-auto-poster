import json


def parse_text(text: str):
    valid_json = text.replace("\\n", "").replace("\n", "")
    return json.loads(valid_json)
