import sqlite3
import json

db_path = r"E:\SWE_Project\Application\backend\instance\clubconnect.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, email, auth_provider, password_hash FROM users")
rows = cursor.fetchall()
result = [dict(row) for row in rows]
print(json.dumps(result, indent=2))
