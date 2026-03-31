import sqlite3

conn = sqlite3.connect('school_report.db')
cursor = conn.cursor()
try:
    cursor.execute('SELECT COUNT(*) FROM custom_exams')
    count = cursor.fetchone()[0]
    print(f'Found {count} exams in database')
except Exception as e:
    print(f'Database error: {e}')
finally:
    conn.close()