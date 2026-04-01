import sqlite3

conn = sqlite3.connect('school_report.db')
c = conn.cursor()

print("=== STUDENTS ===")
c.execute('SELECT admission_no, name, class_name FROM students ORDER BY admission_no')
students = c.fetchall()
for s in students:
    print(f\"Student: {s[0]} - {s[1]} ({s[2]})\")
print(f\"Total students: {len(students)}\\n\")

print(\"=== PT1 MARKS ===\")
c.execute('SELECT student_id, subject, written FROM marks WHERE exam_type=? ORDER BY student_id, subject', ('PT1',))
pt1_marks = c.fetchall()
if pt1_marks:
    for m in pt1_marks:
        print(f\"{m[0]} | {m[1]} | {m[2]}\")
    print(f\"Total PT1 entries: {len(pt1_marks)}\")
else:
    print(\"No PT1 marks found\")

print(\"\\n=== ALL MARKS SUMMARY ===\")
c.execute('SELECT exam_type, COUNT(*) FROM marks GROUP BY exam_type')
exams = c.fetchall()
for e in exams:
    print(f\"{e[0]}: {e[1]} entries\")

conn.close()
print(\"\\nCheck complete!\")

