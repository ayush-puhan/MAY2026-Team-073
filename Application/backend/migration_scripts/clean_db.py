import json
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "db.json"))

def clean_db_json():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    id_mapping = {}  # old_string_id -> new_int_id
    next_id = 10000

    # 1. Identify all non-integer IDs and map them
    for table_name, table_data in data.items():
        if isinstance(table_data, list):
            for row in table_data:
                if isinstance(row, dict) and "id" in row:
                    val = row["id"]
                    try:
                        int(val)
                    except (ValueError, TypeError):
                        if val not in id_mapping:
                            id_mapping[val] = str(next_id)
                            next_id += 1
                        row["id"] = id_mapping[val]

    # 2. Traverse the entire JSON and replace any string values that match id_mapping keys
    def replace_fks(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and v in id_mapping:
                    obj[k] = id_mapping[v]
                else:
                    replace_fks(v)
        elif isinstance(obj, list):
            for item in obj:
                replace_fks(item)

    replace_fks(data)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Cleaned {len(id_mapping)} invalid IDs from db.json.")
    print("Mappings:", id_mapping)

if __name__ == "__main__":
    clean_db_json()
