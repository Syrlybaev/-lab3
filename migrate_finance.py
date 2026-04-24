import sqlite3
import os

db_path = "c:\\Fvus\\ISIT\\lab3_my\\-lab3\\dekanat.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE finance ADD COLUMN teacher_id INTEGER")
    print("Column 'teacher_id' added to 'finance' table.")
except sqlite3.OperationalError:
    print("Column 'teacher_id' already exists.")

conn.commit()
conn.close()
