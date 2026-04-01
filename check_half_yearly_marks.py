import sqlite3
print("=== HALF YEARLY MARKS TABLE ===")
conn = sqlite3.connect('school_report.db')
c = conn.cursor()
c.execute("SELECT student_id, subject, pt, ma, se, pf, written, theory, practical FROM marks WHERE exam_type='Half Yearly'")
rows = c.fetchall()
if not rows:
    print("No Half Yearly marks found in database.")
else:
    print("| Student ID | Subject  | PT | MA | SE | PF | Written | Theory | Practical | Total |")
    print("|------------|----------|----|----|----|----|---------|--------|-----------|-------|")
for row in rows:
        student_id, subject, pt, ma, se, pf, written, theory, practical = (row + (0,0))[:9]
        pt = pt or 0
        ma = ma or 0
        se = se or 0
        pf = pf or 0
        written = written or 0
        theory = theory or 0
        practical = practical or 0
        total = pt + ma + se + pf + written + theory + practical
        print(f"| {student_id:<10} | {subject:<8} | {pt:>3} | {ma:>3} | {se:>3} | {pf:>3} | {written:>7} | {theory:>6} | {practical:>9} | {total:>5} |")
conn.close()
print("\nDatabase query complete.")
