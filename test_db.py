import sqlite3
import os

db_path = "c:\\Fvus\\ISIT\\lab3_my\\-lab3\\dekanat.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
print("Users:", [dict(row) for row in conn.execute("SELECT login FROM users").fetchall()])
# Try to execute delete
conn.execute("DELETE FROM users WHERE login = 'nonexistent'")
conn.commit()
print("Success")
conn.close()
