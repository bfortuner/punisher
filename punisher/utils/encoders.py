import json
import pandas
from enum import Enum
from datetime import datetime, date


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class EnumDecoder(json.JSONDecoder):
    pass
