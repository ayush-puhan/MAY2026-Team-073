import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import get_session

MOCK_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/public/db.json"))

def clean_dict_ids(d):
    keys_to_delete = []
    for k, v in list(d.items()):
        if k.endswith('id') and v is not None:
            try:
                d[k] = int(v)
            except ValueError:
                # If it's a random string ID, it's garbage test data, remove the whole row
                return False
        elif isinstance(v, dict):
            if not clean_dict_ids(v):
                keys_to_delete.append(k)
        elif isinstance(v, list):
            new_list = []
            for item in v:
                if isinstance(item, dict):
                    if clean_dict_ids(item):
                        new_list.append(item)
                else:
                    new_list.append(item)
            d[k] = new_list
    for k in keys_to_delete:
        del d[k]
    return True

def load_mock_data():
    with open(MOCK_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        clean_dict_ids(data)
        return data

def parse_datetime(dt_str):
    if not dt_str: return None
    try:
        # e.g. "2024-03-25T10:00:00Z"
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except Exception:
        # fallback
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d")
        except:
            return None

def parse_date(date_str):
    if not date_str: return None
    try:
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None

def str_to_bool(val):
    if isinstance(val, bool): return val
    if not val: return False
    return str(val).lower() in ["true", "1", "yes"]

def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def clear_all_tables():
    from app.database.database import engine
    from app.database.base import Base
    import app.database.models  # trigger all imports
    # Danger: Drops and recreates all tables to ensure clean slate!
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Dropped and recreated all tables for a clean migration.")

if __name__ == "__main__":
    clear_all_tables()
