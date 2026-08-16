import json
import os

DATA_DIR = "data"
SAVE_FILE = os.path.join(DATA_DIR, "save.json")

DEFAULT_DATA = {
    "highscore": 0
}

def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f)

def load_data():
    ensure_data()
    with open(SAVE_FILE, "r") as f:
        try:
            data = json.load(f)
        except Exception:
            data = DEFAULT_DATA.copy()
    for k, v in DEFAULT_DATA.items():
        if k not in data:
            data[k] = v
    return data

def save_data(data):
    ensure_data()
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_highscore():
    return load_data().get("highscore", 0)

def save_highscore(value):
    data = load_data()
    data["highscore"] = max(value, data.get("highscore", 0))
    save_data(data)
