import sqlite3
import os

db_path = "c:\\Fvus\\ISIT\\lab3_my\\-lab3\\dekanat.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Try to add contacts column
    cursor.execute("ALTER TABLE teachers ADD COLUMN contacts TEXT")
    print("Column 'contacts' added to 'teachers' table.")
except sqlite3.OperationalError:
    print("Column 'contacts' already exists or table doesn't exist.")

conn.commit()
conn.close()
