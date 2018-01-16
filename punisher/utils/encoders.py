import json
import pandas
from enum import Enum
from datetime import datetime, date

from punisher.data.provider import DataProvider


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, DataProvider):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


class EnumDecoder(json.JSONDecoder):
    # TODO: This
    pass
