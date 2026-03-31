import sqlite3
import json

try:
    conn = sqlite3.connect('school_report.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT exam_name, classes, sections, subjects FROM custom_exams')
    rows = cursor.fetchall()
    
    print("=== CUSTOM EXAMS IN DATABASE ===")
    if not rows:
        print("No custom exams found!")
    else:
        for row in rows:
            exam_name = row['exam_name']
            classes = json.loads(row['classes'])
            sections = json.loads(row['sections'])
            subjects = json.loads(row['subjects'])
            print(f"\nExam: {exam_name}")
            print(f"  Classes: {classes}")
            print(f"  Sections: {sections}")
            print(f"  Subjects: {subjects}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
