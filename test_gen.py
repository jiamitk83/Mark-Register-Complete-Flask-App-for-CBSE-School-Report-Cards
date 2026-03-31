import sqlite3

def get_next_admission_no():
    conn = sqlite3.connect('school_report.db')
    cursor = conn.cursor()
    cursor.execute('SELECT admission_no FROM students ORDER BY CAST(admission_no AS INTEGER) DESC LIMIT 1')
    last_admission = cursor.fetchone()
    conn.close()
    
    if last_admission:
        try:
            last_num = int(last_admission[0])
            return f'ADM{last_num + 1:03d}'
        except ValueError:
            return 'ADM001'
    else:
        return 'ADM001'

print('Next admission number:', get_next_admission_no())