"""Script to add dummy marks data for testing"""
import sqlite3
import json

DATABASE = 'mark_register.db'

def add_dummy_marks():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get existing students
    cursor.execute('SELECT id, name FROM students LIMIT 10')
    students = cursor.fetchall()
    print(f"Found {len(students)} students")
    
    # Get existing subjects
    cursor.execute('SELECT id, name FROM subjects')
    subjects = cursor.fetchall()
    print(f"Found {len(subjects)} subjects")
    
    if not students or not subjects:
        print("No students or subjects found. Please add them first.")
        conn.close()
        return
    
    # Add dummy marks for each student
    exam_types = ['FA1', 'FA2', 'SA1']
    added = 0
    
    for student_id, student_name in students:
        for subject_id, subject_name in subjects:
            for exam_type in exam_types:
                # Generate random marks (out of 100)
                import random
                marks = random.randint(60, 95)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject_id, marks, exam_type)
                    VALUES (?, ?, ?, ?)
                ''', (student_id, subject_id, marks, exam_type))
                added += 1
    
    conn.commit()
    print(f"Added {added} dummy marks entries")
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM marks')
    count = cursor.fetchone()[0]
    print(f"Total marks in database: {count}")
    
    conn.close()

if __name__ == '__main__':
    add_dummy_marks()
