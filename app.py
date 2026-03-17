"""
School Mark Register Web Application
A comprehensive web app for managing student marks, subjects, and grades.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'mark_register_secret_key_2024'

# Database configuration
DATABASE = 'mark_register.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            term TEXT DEFAULT '2024-25',
            grade TEXT,
            section TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Safe migration - only add columns if they don't exist
    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'term' not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN term TEXT DEFAULT '2024-25'")
    if 'grade' not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN grade TEXT")
    if 'section' not in columns:
        cursor.execute("ALTER TABLE students ADD COLUMN section TEXT")
    
    # Migration for existing students
    cursor.execute("""
        UPDATE students SET 
            grade = CASE WHEN grade IS NULL AND class_name LIKE '%-%' THEN SUBSTR(class_name, 1, INSTR(class_name || '-', '-') - 1) ELSE grade END,
            section = CASE WHEN section IS NULL AND class_name LIKE '%-%' THEN TRIM(SUBSTR(class_name, INSTR(class_name, '-') + 1)) ELSE section END
        WHERE class_name IS NOT NULL AND class_name != ''
    """)
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Marks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            marks REAL NOT NULL,
            exam_type TEXT DEFAULT 'terminal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(student_id, subject_id, exam_type)
        )
    ''')
    
    # Exam Max Marks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_max_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_type TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            max_marks INTEGER NOT NULL DEFAULT 100,
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(exam_type, subject_id)
        )
    ''')
    
    # Default 4 exams for each subject (add if subjects exist)
    cursor.execute('SELECT id FROM subjects')
    subjects = cursor.fetchall()
    exams = ['TERM1', 'TERM2', 'MIDTERM', 'FINAL']
    default_max = {'TERM1': 50, 'TERM2': 50, 'MIDTERM': 70, 'FINAL': 100}
    
    for subject in subjects:
        for exam in exams:
            cursor.execute('''
                INSERT OR IGNORE INTO exam_max_marks (exam_type, subject_id, max_marks)
                VALUES (?, ?, ?)
            ''', (exam, subject['id'], default_max[exam]))
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # Insert default settings if not exists
    default_settings = [
        ('passing_marks', '35'),
        ('grade_A+', '90'),
        ('grade_A', '80'),
        ('grade_B+', '70'),
        ('grade_B', '60'),
        ('grade_C', '50'),
        ('grade_D', '40'),
        ('grade_F', '0')
    ]
    
    for key, value in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'

# Routes

@app.route('/')
def index():
    """Home page - Dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM marks")
    total_marks_entries = cursor.fetchone()[0]
    
    # Get recent students
    cursor.execute("""
        SELECT * FROM students 
        ORDER BY created_at DESC LIMIT 5
    """)
    recent_students = cursor.fetchall()
    
    # Get all subjects
    cursor.execute("SELECT * FROM subjects ORDER BY name")
    subjects = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                           total_students=total_students,
                           total_subjects=total_subjects,
                           total_marks_entries=total_marks_entries,
                           recent_students=recent_students,
                           subjects=subjects)

# Student routes
@app.route('/students')
def students_page():
    """Students management page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY class_name, name")
    students = cursor.fetchall()
    conn.close()
    return render_template('students.html', students=students)

@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    """API for students CRUD"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            # Generate auto student_id S001, S002...
            cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTR(student_id, 2) AS INTEGER)), 0) + 1 as next_id FROM students WHERE student_id LIKE 'S%'")
            next_num = cursor.fetchone()['next_id']
            student_id = f"S{next_num:03d}"
            
            cursor.execute('''
                INSERT INTO students (student_id, name, class_name)
                VALUES (?, ?, ?)
            ''', (student_id, data['name'].title(), data['class_name'].title()))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': f'Student {student_id} added successfully!', 'student_id': student_id})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Student ID already exists!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)})
    
    # GET request
    cursor.execute("SELECT * FROM students ORDER BY class_name, name")
    students = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Student deleted successfully!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/students/bulk', methods=['POST'])
def api_students_bulk():
    """Bulk upload students from CSV"""
    if 'csv_file' not in request.files:
        return jsonify({'success': False, 'message': 'No CSV file provided'})
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get next student ID
        cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTR(student_id, 2) AS INTEGER)), 0) + 1 as next_num FROM students WHERE student_id LIKE 'S%'")
        next_num = cursor.fetchone()[0]
        
        added = 0
        skipped = 0
        
        import io
        import csv
        
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.reader(stream)
        
        for row_num, row in enumerate(reader, 1):
            if len(row) < 2 or not row[0].strip():
                skipped += 1
                continue
            
            name = row[0].strip().title()
            class_name = row[1].strip().title()
            
            if len(name) < 2:
                skipped += 1
                continue
            
            student_id = f"S{next_num:03d}"
            try:
                cursor.execute('''
                    INSERT INTO students (student_id, name, class_name)
                    VALUES (?, ?, ?)
                ''', (student_id, name, class_name))
                next_num += 1
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Bulk upload complete! Added: {added}, Skipped: {skipped}'
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

# Subject routes
@app.route('/subjects')
def subjects_page():
    """Subjects management page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY name")
    subjects = cursor.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

@app.route('/api/subjects', methods=['GET', 'POST'])
def api_subjects():
    """API for subjects CRUD"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute('INSERT INTO subjects (name) VALUES (?)', (data['name'].title(),))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Subject added successfully!'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Subject already exists!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)})
    
    # GET request
    cursor.execute("SELECT * FROM subjects ORDER BY name")
    subjects = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in subjects])

# === CASCADE FILTER APIs ===
@app.route('/api/filters/terms')
def api_filters_terms():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT term FROM students WHERE term IS NOT NULL ORDER BY term DESC")
    terms = [row['term'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(terms or ['2024-25'])

@app.route('/api/filters/grades')
def api_filters_grades():
    term = request.args.get('term')
    conn = get_db()
    cursor = conn.cursor()
    if term:
        cursor.execute("SELECT DISTINCT grade FROM students WHERE term = ? AND grade IS NOT NULL AND grade != '' ORDER BY grade", (term,))
    else:
        cursor.execute("SELECT DISTINCT grade FROM students WHERE grade IS NOT NULL AND grade != '' ORDER BY grade")
    grades = [row['grade'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(grades)

@app.route('/api/filters/sections')
def api_filters_sections():
    term = request.args.get('term')
    grade = request.args.get('grade')
    conn = get_db()
    cursor = conn.cursor()
    params = []
    query = "SELECT DISTINCT section FROM students WHERE section IS NOT NULL AND section != ''"
    if term:
        query += " AND term = ?"
        params.append(term)
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    query += " ORDER BY section"
    cursor.execute(query, params)
    sections = [row['section'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(sections)

@app.route('/api/students/group')
def api_students_group():
    """Students for cascade selection"""
    term = request.args.get('term')
    grade = request.args.get('grade')
    section = request.args.get('section')
    conn = get_db()
    cursor = conn.cursor()
    params = []
    query = "SELECT student_id, name, class_name, grade, section FROM students WHERE 1=1"
    if term:
        query += " AND term = ?"
        params.append(term)
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    if section:
        query += " AND section = ?"
        params.append(section)
    query += " ORDER BY name"
    cursor.execute(query, params)
    students = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.route('/api/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete a subject"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM marks WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Subject deleted successfully!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

# Marks routes
@app.route('/marks')
def marks_page():
    """Marks entry page"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students ORDER BY class_name, name")
    students = cursor.fetchall()
    
    cursor.execute("""
        SELECT s.*, 
               COALESCE(e1.max_marks, 50) as max_term1,
               COALESCE(e2.max_marks, 50) as max_term2,
               COALESCE(e3.max_marks, 70) as max_midterm,
               COALESCE(e4.max_marks, 100) as max_final
        FROM subjects s
        LEFT JOIN exam_max_marks e1 ON s.id = e1.subject_id AND e1.exam_type = 'TERM1'
        LEFT JOIN exam_max_marks e2 ON s.id = e2.subject_id AND e2.exam_type = 'TERM2'
        LEFT JOIN exam_max_marks e3 ON s.id = e3.subject_id AND e3.exam_type = 'MIDTERM'
        LEFT JOIN exam_max_marks e4 ON s.id = e4.subject_id AND e4.exam_type = 'FINAL'
        ORDER BY s.name
    """)
    subjects = cursor.fetchall()
    
    # Get existing marks
    cursor.execute('''
        SELECT m.*, s.name as subject_name, st.name as student_name, st.class_name
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        JOIN students st ON m.student_id = st.student_id
        ORDER BY st.name, s.name, m.exam_type
    ''')
    marks = cursor.fetchall()
    
    conn.close()
    return render_template('marks.html', students=students, subjects=subjects, marks=marks)

# Settings routes
@app.route('/settings')
def settings_page():
    """Settings page"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get current settings
    cursor.execute('SELECT key, value FROM settings')
    settings_rows = cursor.fetchall()
    settings = {row[0]: row[1] for row in settings_rows}
    
    conn.close()
    return render_template('settings.html', settings=settings)

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """API to get or save settings"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            for key, value in data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES (?, ?)
                ''', (key, str(value)))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Settings saved successfully!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)})
    else:
        # GET - return all settings
        cursor.execute('SELECT key, value FROM settings')
        settings_rows = cursor.fetchall()
        settings = {row[0]: row[1] for row in settings_rows}
        conn.close()
        return jsonify(settings)

# Results routes
@app.route('/results')
def results_page():
    """Results page"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all terms
    cursor.execute('SELECT DISTINCT term FROM students ORDER BY term')
    terms = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('results.html', terms=terms)

# Bulk marks save API (Step 5)
@app.route('/api/marks/bulk-group', methods=['POST'])
def api_marks_bulk_group():
    """Bulk save marks for group of students"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        term = data['term']
        grade = data['grade']
        section = data['section']
        subject_id = data['subject_id']
        marks_data = data['marks_data']
        
        added = 0
        updated = 0
        errors = 0
        
        for student_id, exams in marks_data.items():
            for exam_type, marks in exams.items():
                if marks > 0:  # Only save non-zero marks
                    cursor.execute('''
                        INSERT OR REPLACE INTO marks (student_id, subject_id, marks, exam_type)
                        VALUES (?, ?, ?, ?)
                    ''', (student_id, subject_id, marks, exam_type))
                    if cursor.rowcount > 0:
                        updated += 1

        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'message': f'Bulk marks saved! Updated: {updated}, Added: {added}',
            'count': len(marks_data)
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

# Single mark save API
@app.route('/api/marks', methods=['POST'])
def api_marks():
    """Save a single mark entry"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        marks = data.get('marks')
        exam_type = data.get('exam_type')
        
        if not all([student_id, subject_id, marks is not None, exam_type]):
            conn.close()
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        cursor.execute('''
            INSERT OR REPLACE INTO marks (student_id, subject_id, marks, exam_type)
            VALUES (?, ?, ?, ?)
        ''', (student_id, subject_id, marks, exam_type))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Mark saved successfully!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

# Max marks API for settings page
@app.route('/api/maxmarks', methods=['GET', 'POST'])
def api_maxmarks():
    """Get or save maximum marks for exams"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json()
        try:
            matrix = data.get('matrix', [])
            for item in matrix:
                exam_type = item.get('exam_type')
                subject_id = item.get('subject_id')
                max_marks = item.get('max_marks')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO exam_max_marks (subject_id, exam_type, max_marks)
                    VALUES (?, ?, ?)
                ''', (subject_id, exam_type, max_marks))
            
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Max marks saved!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)})
    else:
        # GET - return matrix
        cursor.execute('''
            SELECT s.id, s.name, e.exam_type, e.max_marks
            FROM subjects s
            LEFT JOIN exam_max_marks e ON s.id = e.subject_id
            ORDER BY s.name
        ''')
        rows = cursor.fetchall()
        
        # Transform to matrix format
        subjects = {}
        for row in rows:
            subject_id = row['id']
            if subject_id not in subjects:
                subjects[subject_id] = {
                    'id': subject_id,
                    'name': row['name'],
                    'TERM1': None,
                    'TERM2': None,
                    'MIDTERM': None,
                    'FINAL': None
                }
            if row['exam_type']:
                subjects[subject_id][row['exam_type']] = row['max_marks']
        
        # Add exam type info
        matrix = []
        for sid, subj in subjects.items():
            matrix.append({
                'id': subj['id'],
                'name': subj['name'],
                'TERM1': subj.get('TERM1') or 50,
                'TERM1_exam': 'TERM1',
                'TERM1_subject': subj['id'],
                'TERM2': subj.get('TERM2') or 50,
                'TERM2_exam': 'TERM2',
                'TERM2_subject': subj['id'],
                'MIDTERM': subj.get('MIDTERM') or 70,
                'MIDTERM_exam': 'MIDTERM',
                'MIDTERM_subject': subj['id'],
                'FINAL': subj.get('FINAL') or 100,
                'FINAL_exam': 'FINAL',
                'FINAL_subject': subj['id']
            })
        
        conn.close()
        return jsonify({'matrix': matrix})


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
