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


def save_json(fpath, dict_):
    with open(fpath, 'w') as f:
        json.dump(dict_, f, indent=4, cls=EnumEncoder, ensure_ascii=False)

def load_json(fpath):
    with open(fpath, 'r') as f:
        json_ = json.load(f)
    return json_
