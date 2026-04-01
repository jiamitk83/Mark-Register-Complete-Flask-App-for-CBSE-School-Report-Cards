import sqlite3
conn = sqlite3.connect('school_report.db')
c = conn.cursor()
c.execute("SELECT student_id, subject, pt, ma, se, pf, written FROM marks WHERE exam_type='Half Yearly' ORDER BY student_id, subject LIMIT 10")
print('Half Yearly marks:')
for row in c.fetchall():
    print(dict(zip([d[0] for d in c.description], row)))
conn.close()
