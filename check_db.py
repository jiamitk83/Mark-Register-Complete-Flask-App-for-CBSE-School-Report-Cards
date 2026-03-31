import sqlite3
conn = sqlite3.connect('school_report.db')
c = conn.cursor()
c.execute('SELECT admission_no FROM students ORDER BY admission_no')
rows = c.fetchall()
print([row[0] for row in rows])
conn.close()