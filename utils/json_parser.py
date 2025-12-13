import json
import logging


def parse_text(text: str, default=None) -> list:
    try:
        valid_json = text.replace("\\n", "").replace("\n", "")
        return json.loads(valid_json)
    except Exception as e:
        logging.warning(e)
        return default
