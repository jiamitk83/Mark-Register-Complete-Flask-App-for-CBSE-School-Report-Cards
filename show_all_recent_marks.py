import sqlite3
from datetime import datetime
print("=== ALL RECENT MARKS FROM DATABASE (Last 20 entries) ===")
conn = sqlite3.connect('school_report.db')
c = conn.cursor()
c.execute("SELECT student_id, subject, exam_type, pt, ma, se, pf, written, theory, practical, created_at FROM marks ORDER BY created_at DESC LIMIT 20")
rows = c.fetchall()
print("| Student | Subject | Exam Type    | PT | MA | SE | PF | Written | Theory | Practical | Created     |")
print("|---------|---------|--------------|----|----|----|----|---------|--------|-----------|-------------|")
if not rows:
    print("No marks found.")
else:
    for row in rows:
        values = list(row[:10]) + [row[10][:16] if row[10] else '']
        student_id, subject, exam_type, pt, ma, se, pf, written, theory, practical, created = values
        pt = pt or 0
        ma = ma or 0
        se = se or 0
        pf = pf or 0
        written = written or 0
        theory = theory or 0
        practical = practical or 0
        print(f"| {student_id:<7} | {subject:<7} | {exam_type:<12} | {pt:>3} | {ma:>3} | {se:>3} | {pf:>3} | {written:>7} | {theory:>6} | {practical:>9} | {created:<11} |")
conn.close()
print("\nUse 'Half Yearly' in bulk-marks for PT/MA/SE/PF/Written breakdown.")
