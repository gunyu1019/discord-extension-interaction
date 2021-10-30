import json

try:
    import orjson
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

if HAS_ORJSON:
    _from_json = orjson.loads
else:
    _from_json = json.loads
