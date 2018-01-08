import json
from enum import Enum
from datetime import datetime, date

import pandas
import utils.dates


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class EnumDecoder(json.JSONDecoder):
    # TODO: This
    pass
