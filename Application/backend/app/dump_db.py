import sqlite3
import json

def dump_db():
    conn = sqlite3.connect('E:/SWE_Project/Application/backend/app/database/clubconnect.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall() if row['name'] != 'sqlite_sequence']
    
    db_dict = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        db_dict[table] = rows
        
    with open('E:/SWE_Project/Application/frontend/public/db.json', 'w') as f:
        json.dump(db_dict, f, indent=2)
        
    print(f"Dumped {len(tables)} tables to db.json")

dump_db()
