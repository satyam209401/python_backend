import base64
import json


def d(data, as_json=False):
    if not data:
        return None

    try:
        raw = base64.b64decode(data.strip(), validate=True)
        text = raw.decode("utf-8")
        return json.loads(text) if as_json else text

    except UnicodeDecodeError:
        return raw

    except (ValueError, TypeError, json.JSONDecodeError):
        return None
