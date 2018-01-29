import json
from .encoders import EnumEncoder

def save_dct(fpath, dct, mode='w'):
    with open(fpath, mode) as f:
        json.dump(
            dct, f, indent=4,
            cls=EnumEncoder,
            ensure_ascii=False)

def save_str(fpath, string, mode='w'):
    with open(fpath, mode) as f:
        f.write(string)

def load_json(fpath):
    with open(fpath, 'r') as f:
        json_ = json.load(f)
    return json_
