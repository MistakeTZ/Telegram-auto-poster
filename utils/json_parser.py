import json


def parse_text(text: str) -> list:
    valid_json = text.replace("\\n", "").replace("\n", "")
    return json.loads(valid_json)
