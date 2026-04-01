import sqlite3

conn = sqlite3.connect('school_report.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("All tables in the database:")
for table in tables:
    print(f"  - {table[0]}")
conn.close()