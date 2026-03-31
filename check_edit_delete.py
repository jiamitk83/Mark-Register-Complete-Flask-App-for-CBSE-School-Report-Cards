import sqlite3
import json

conn = sqlite3.connect('school_report.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check custom exams
cursor.execute('SELECT exam_name, max_marks, created_at FROM custom_exams')
exams = cursor.fetchall()

if exams:
    print(f'Found {len(exams)} custom exams:')
    for exam in exams:
        print(f'  - {exam[0]} (Max: {exam[1]}, Created: {exam[2]})')
else:
    print('No custom exams found in database')

conn.close()
