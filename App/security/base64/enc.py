
import base64
import json


def e(data):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode("utf-8")

    return base64.b64encode(data).decode("ascii")
