"""
CBSE School Report Card Web Application
A comprehensive web app for managing student marks and generating report cards.
Based on CBSE assessment patterns with PT, MA, SE, PF, and Written exams.
"""
with open('debug_startup.log', 'w') as f:
    f.write("Starting app.py\n")
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
with open('debug_startup.log', 'a') as f:
    f.write("Imports done\n")
import sqlite3
import os
from datetime import datetime, date

with open('debug_startup.log', 'a') as f:
    f.write("Creating Flask app\n")
app = Flask(__name__)

# Secret key should be set via environment in production
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    if os.getenv('FLASK_ENV') == 'production' or os.getenv('ENV') == 'production':
        raise RuntimeError('SECRET_KEY environment variable is required in production')
    secret_key = 'dev_secret_key_please_change'
app.secret_key = secret_key

# Database configuration
DATABASE = 'school_report.db'

# Subject list
SUBJECTS = ['English', 'Hindi', 'Maths', 'Science', 'SST', 'Computer', 'French']

def clamp_mark(value, max_val):
    try:
        mark = float(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, min(mark, max_val))

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with CBSE schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL,
            roll_no INTEGER,
            father_name TEXT,
            mother_name TEXT,
            dob TEXT,
            term TEXT DEFAULT '2024-25',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Marks table - CBSE format with PT, MA, SE, PF, Written for Half Yearly and Final
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,  -- 'Half Yearly' or 'Final' or custom exam name
            pt REAL DEFAULT 0,         -- Periodic Test
            ma REAL DEFAULT 0,         -- Multiple Assessment
            se REAL DEFAULT 0,         -- Subject Enrichment
            pf REAL DEFAULT 0,         -- Portfolio
            written REAL DEFAULT 0,   -- Written Exam
            theory REAL DEFAULT 0,     -- Theory marks (for Computer)
            practical REAL DEFAULT 0,  -- Practical marks (for Computer)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(admission_no),
            UNIQUE(student_id, subject, exam_type)
        )
    ''')
    
    # Add theory and practical columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE marks ADD COLUMN theory REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE marks ADD COLUMN practical REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Custom exams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT UNIQUE NOT NULL,
            classes TEXT NOT NULL,  -- JSON array of classes
            sections TEXT NOT NULL, -- JSON array of sections
            subjects TEXT NOT NULL, -- JSON array of subjects
            students TEXT,          -- JSON array of student IDs (optional, if not specified use all matching criteria)
            max_marks REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_total(pt, ma, se, pf, written, subject='Other', theory=0, practical=0):
    """Calculate subject total"""
    if subject.lower() == 'computer':
        return theory + practical
    else:
        return pt + ma + se + pf + written

def calculate_weighted_score(hy_total, final_total):
    """Calculate weighted score: 40% Half Yearly + 60% Final"""
    return (hy_total * 0.4) + (final_total * 0.6)

def assign_grade(percentage):
    """Assign grade based on CBSE percentage"""
    if percentage >= 91:
        return 'A1'
    elif percentage >= 81:
        return 'A2'
    elif percentage >= 71:
        return 'B1'
    elif percentage >= 61:
        return 'B2'
    elif percentage >= 51:
        return 'C1'
    elif percentage >= 41:
        return 'C2'
    elif percentage >= 33:
        return 'D'
    else:
        return 'E'

def get_remarks(grade, percentage):
    """Generate remarks based on grade and percentage"""
    remarks_map = {
        'A1': 'Outstanding performance! Keep up the excellent work.',
        'A2': 'Excellent performance. Very good work.',
        'B1': 'Very good performance. Keep improving.',
        'B2': 'Good performance. Continue working hard.',
        'C1': 'Satisfactory performance. Need more practice.',
        'C2': 'Needs improvement. Work on weaker areas.',
        'D': 'Needs extra attention. Focus on studies.',
        'E': 'Requires urgent improvement. Need remedial classes.'
    }
    return remarks_map.get(grade, 'Keep working hard.')

# Initialize database
try:
    with open('debug_startup.log', 'a') as f:
        f.write("Initializing database...\n")
    init_db()
    with open('debug_startup.log', 'a') as f:
        f.write("Database initialized successfully\n")
except Exception as e:
    with open('debug_startup.log', 'a') as f:
        f.write(f"Error initializing database: {e}\n")
    import traceback
    traceback.print_exc()

with open('debug_startup.log', 'a') as f:
    f.write("Starting routes definition\n")
# ==================== SUBJECT MANAGEMENT ====================

def get_subjects():
    """Get active subjects from DB"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects WHERE active = 1 ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    return [dict(s) for s in subjects]

def init_subjects():
    """Initialize default subjects if none exist"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] == 0:
        default_subjects = [
            ('English', 1), ('Hindi', 1), ('Maths', 1), ('Science', 1),
            ('SST', 1), ('Computer', 1), ('French', 1)
        ]
        cursor.executemany('INSERT INTO subjects (name, active) VALUES (?, ?)', default_subjects)
        conn.commit()
    conn.close()

@app.route('/subjects', methods=['GET'])
def subjects_list():
    """List all subjects"""
    init_subjects()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

@app.route('/add-subject', methods=['POST'])
def add_subject():
    """Add new subject"""
    name = request.form.get('subject_name', '').strip().title()
    if not name:
        flash('Subject name required', 'error')
        return redirect(url_for('subjects_list'))
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO subjects (name, active) VALUES (?, 1)', (name,))
        conn.commit()
        flash(f'"{name}" added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Subject already exists!', 'error')
    finally:
        conn.close()
    return redirect(url_for('subjects_list'))

@app.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    """Edit subject"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,))
    subject = cursor.fetchone()
    
    if not subject:
        flash('Subject not found!', 'error')
        return redirect(url_for('subjects_list'))
    
    if request.method == 'POST':
        new_name = request.form.get('subject_name', '').strip().title()
        if new_name:
            cursor.execute('UPDATE subjects SET name = ? WHERE id = ?', (new_name, subject_id))
            conn.commit()
            flash('Subject updated!', 'success')
            conn.close()
            return redirect(url_for('subjects_list'))
    
    conn.close()
    return render_template('edit_subject.html', subject=dict(subject))

@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    """Delete subject"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM subjects WHERE id = ?', (subject_id,))
    subject = cursor.fetchone()
    
    if subject:
        cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        conn.commit()
        flash(f'{subject["name"]} deleted!', 'success')
    
    conn.close()
    return redirect(url_for('subjects_list'))

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page - Dashboard"""

    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT DISTINCT class_name FROM students ORDER BY class_name')
    classes = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('index.html', 
                         total_students=total_students,
                         classes=classes,
                         subjects=SUBJECTS)

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    """Add new student"""
    if request.method == 'POST':
        # Auto-generate admission number
        conn = get_db()
        cursor = conn.cursor()
        # Use numeric suffix of admission_no (ADM###) for proper ordering
        cursor.execute("SELECT admission_no FROM students ORDER BY CAST(SUBSTR(admission_no, 4) AS INTEGER) DESC LIMIT 1")
        last_admission = cursor.fetchone()

        if last_admission and last_admission[0]:
            admission_no_str = last_admission[0]
            suffix = admission_no_str[3:] if len(admission_no_str) > 3 else ''
            try:
                last_num = int(suffix)
                admission_no = f'ADM{last_num + 1:03d}'
            except (ValueError, TypeError):
                # If no numeric suffix, start from ADM001
                admission_no = 'ADM001'
        else:
            admission_no = 'ADM001'
        
        name = request.form.get('name').upper() if request.form.get('name') else ''
        class_name = request.form.get('class_name')
        section = request.form.get('section')
        roll_no = request.form.get('roll_no')
        father_name = request.form.get('father_name').upper() if request.form.get('father_name') else ''
        mother_name = request.form.get('mother_name').upper() if request.form.get('mother_name') else ''
        dob = request.form.get('dob')
        
        try:
            cursor.execute('''
                INSERT INTO students (admission_no, name, class_name, section, roll_no, father_name, mother_name, dob)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (admission_no, name, class_name, section, roll_no, father_name, mother_name, dob))
            conn.commit()
            flash('Student added successfully! Admission Number: ' + admission_no, 'success')
            return redirect(url_for('students'))
        except sqlite3.IntegrityError:
            flash('Error adding student. Please try again.', 'error')
        finally:
            conn.close()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY class_name, section, roll_no, name')
    students_list = cursor.fetchall()
    conn.close()

    return render_template('add_student.html', students=students_list)

@app.route('/students')
def students():
    """View all students"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY class_name, section, roll_no')
    students = cursor.fetchall()
    conn.close()
    return render_template('students.html', students=students)

@app.route('/delete-student/<admission_no>', methods=['POST'])
def delete_student(admission_no):
    """Delete a student"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if student exists
    cursor.execute('SELECT 1 FROM students WHERE admission_no = ?', (admission_no,))
    if not cursor.fetchone():
        conn.close()
        flash('Student not found!', 'error')
        return redirect(url_for('students'))
    
    try:
        cursor.execute('DELETE FROM students WHERE admission_no = ?', (admission_no,))
        cursor.execute('DELETE FROM marks WHERE student_id = ?', (admission_no,))
        conn.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('students'))

@app.route('/edit-student/<admission_no>', methods=['GET', 'POST'])
def edit_student(admission_no):
    """Edit student details"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip().upper()
        class_name = request.form.get('class_name', '').strip()
        section = request.form.get('section', '').strip().upper()
        roll_no_str = request.form.get('roll_no', '')
        father_name = request.form.get('father_name', '').strip().upper()
        mother_name = request.form.get('mother_name', '').strip().upper()
        dob = request.form.get('dob', '').strip()
        
        roll_no = int(roll_no_str) if roll_no_str.isdigit() else None
        
        # Validation
        if not name or not class_name or not section:
            flash('Name, Class, and Section are required!', 'error')
            cursor.execute('SELECT * FROM students WHERE admission_no = ?', (admission_no,))
            student = cursor.fetchone()
            if not student:
                conn.close()
                flash('Student not found!', 'error')
                return redirect(url_for('students'))
            conn.close()
            return render_template('edit_student.html', student=dict(student))
        
        try:
            cursor.execute(''' 
                UPDATE students SET 
                    name = ?, class_name = ?, section = ?, roll_no = ?, 
                    father_name = ?, mother_name = ?, dob = ?
                WHERE admission_no = ?
            ''', (name, class_name, section, roll_no, father_name, mother_name, dob, admission_no))
            conn.commit()
            flash(f'Student "{name}" updated successfully!', 'success')
        except sqlite3.Error as e:
            flash(f'Error updating student: {str(e)}', 'error')
        finally:
            conn.close()
        return redirect(url_for('students'))
    
    # GET: Show edit form
    cursor.execute('SELECT * FROM students WHERE admission_no = ?', (admission_no,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('students'))
    
    return render_template('edit_student.html', student=dict(student), today=date.today().isoformat())

@app.route('/enter-marks', methods=['GET', 'POST'])
def enter_marks():
    """Enter marks for students"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject = request.form.get('subject')
        
        exam_type = request.form.get('exam_type', 'Half Yearly')
        
        if exam_type not in ['Half Yearly', 'Final'] and exam_type != 'Both':
            # Custom exam - single written mark
            marks = clamp_mark(request.form.get('marks'), 100)  # Default max, actual validated via JS
            cursor.execute('''
                INSERT OR REPLACE INTO marks (student_id, subject, exam_type, written)
                VALUES (?, ?, ?, ?)
            ''', (student_id, subject, exam_type, marks))
            conn.commit()
            flash(f'{exam_type} marks saved for {subject}!', 'success')
            conn.close()
            return redirect(url_for('enter_marks'))
        
        # Standard HY/Final handling (Both saves both)
        if exam_type in ['Half Yearly', 'Both']:
            if subject.lower() == 'computer':
                hy_theory = clamp_mark(request.form.get('hy_theory'), 70)
                hy_practical = clamp_mark(request.form.get('hy_practical'), 30)
                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject, exam_type, theory, practical)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, subject, 'Half Yearly', hy_theory, hy_practical))
            else:
                hy_pt = clamp_mark(request.form.get('hy_pt'), 5)
                hy_ma = clamp_mark(request.form.get('hy_ma'), 5)
                hy_se = clamp_mark(request.form.get('hy_se'), 5)
                hy_pf = clamp_mark(request.form.get('hy_pf'), 5)
                hy_written = clamp_mark(request.form.get('hy_written'), 80)
                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject, exam_type, pt, ma, se, pf, written)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, subject, 'Half Yearly', hy_pt, hy_ma, hy_se, hy_pf, hy_written))
        
        if exam_type in ['Final', 'Both']:
            if subject.lower() == 'computer':
                final_theory = clamp_mark(request.form.get('final_theory'), 70)
                final_practical = clamp_mark(request.form.get('final_practical'), 30)
                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject, exam_type, theory, practical)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, subject, 'Final', final_theory, final_practical))
            else:
                final_pt = clamp_mark(request.form.get('final_pt'), 5)
                final_ma = clamp_mark(request.form.get('final_ma'), 5)
                final_se = clamp_mark(request.form.get('final_se'), 5)
                final_pf = clamp_mark(request.form.get('final_pf'), 5)
                final_written = clamp_mark(request.form.get('final_written'), 80)
                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject, exam_type, pt, ma, se, pf, written)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, subject, 'Final', final_pt, final_ma, final_se, final_pf, final_written))
        
        conn.commit()
        flash(f'{exam_type} marks saved for {subject}!', 'success')
        conn.close()
        return redirect(url_for('enter_marks'))
    
# Get all students for dropdown with class/section for filtering
    cursor.execute('SELECT admission_no, name, class_name, section FROM students ORDER BY class_name, name')
    students = cursor.fetchall()

    # Get custom exams for dropdown (like bulk_marks)
    cursor.execute('SELECT exam_name, max_marks, subjects, classes, sections FROM custom_exams ORDER BY created_at DESC')
    raw_custom_exams = cursor.fetchall()
    custom_exams = []
    import json
    for row in raw_custom_exams:
        exam = dict(row)
        exam['classes'] = json.loads(exam['classes'])
        exam['sections'] = json.loads(exam['sections'])
        exam['subjects'] = json.loads(exam['subjects'])
        custom_exams.append(exam)
    
    conn.close()
    
    return render_template('enter_marks.html', students=students, subjects=SUBJECTS, custom_exams=custom_exams)

@app.route('/bulk-marks', methods=['GET', 'POST'])
def bulk_marks():
    """Bulk enter marks for a class"""
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        section = request.form.get('section')
        subject = request.form.get('subject')
        exam_type = request.form.get('exam_type') or 'Both'

        # Get all students in the class
        cursor.execute('SELECT admission_no, name FROM students WHERE class_name = ? AND section = ? ORDER BY roll_no',
                       (class_name, section))
        students = cursor.fetchall()

        # Custom exam support
        if exam_type not in ['Both', 'Half Yearly', 'Final']:
            cursor.execute('SELECT * FROM custom_exams WHERE exam_name = ?', (exam_type,))
            custom_exam = cursor.fetchone()
            if not custom_exam:
                flash('Selected custom exam not found.', 'error')
                conn.close()
                return redirect(url_for('bulk_marks'))

            import json
            custom_subjects = json.loads(custom_exam['subjects'])
            max_marks = custom_exam['max_marks']

            if subject not in custom_subjects:
                flash(f'Subject {subject} is not part of the selected exam {exam_type}.', 'error')
                conn.close()
                return redirect(url_for('bulk_marks'))

            for student in students:
                student_id = student['admission_no']
                mark = float(request.form.get(f'custom_mark_{student_id}', 0) or 0)
                if mark < 0:
                    mark = 0
                if mark > max_marks:
                    mark = max_marks

                cursor.execute('''
                    INSERT OR REPLACE INTO marks (student_id, subject, exam_type, written)
                    VALUES (?, ?, ?, ?)
                ''', (student_id, subject, exam_type, mark))

            conn.commit()
            flash(f'Bulk marks saved for Class {class_name} Section {section} ({subject}, {exam_type})!', 'success')
            conn.close()
            return redirect(url_for('bulk_marks'))

        saved_count = 0
        print(f"Bulk save: {len(students)} students, {subject}, {exam_type}")
        
        for student in students:
            student_id = student['admission_no']

            if subject.lower() == 'computer':
                if exam_type in ['Half Yearly', 'Both']:
                    theory = clamp_mark(request.form.get(f'hy_theory_{student_id}'), 70)
                    practical = clamp_mark(request.form.get(f'hy_practical_{student_id}'), 30)
                    cursor.execute('''
                        INSERT OR REPLACE INTO marks (student_id, subject, exam_type, theory, practical)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, subject, 'Half Yearly', theory, practical))
                    saved_count += 1
                if exam_type in ['Final', 'Both']:
                    theory = clamp_mark(request.form.get(f'final_theory_{student_id}'), 70)
                    practical = clamp_mark(request.form.get(f'final_practical_{student_id}'), 30)
                    cursor.execute('''
                        INSERT OR REPLACE INTO marks (student_id, subject, exam_type, theory, practical)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, subject, 'Final', theory, practical))
                    saved_count += 1
            else:
                if exam_type in ['Half Yearly', 'Both']:
                    pt = clamp_mark(request.form.get(f'hy_pt_{student_id}'), 5)
                    ma = clamp_mark(request.form.get(f'hy_ma_{student_id}'), 5)
                    se = clamp_mark(request.form.get(f'hy_se_{student_id}'), 5)
                    pf = clamp_mark(request.form.get(f'hy_pf_{student_id}'), 5)
                    written = clamp_mark(request.form.get(f'hy_written_{student_id}'), 80)
                    cursor.execute('''
                        INSERT OR REPLACE INTO marks (student_id, subject, exam_type, pt, ma, se, pf, written)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (student_id, subject, 'Half Yearly', pt, ma, se, pf, written))
                    saved_count += 1
                if exam_type in ['Final', 'Both']:
                    pt = clamp_mark(request.form.get(f'final_pt_{student_id}'), 5)
                    ma = clamp_mark(request.form.get(f'final_ma_{student_id}'), 5)
                    se = clamp_mark(request.form.get(f'final_se_{student_id}'), 5)
                    pf = clamp_mark(request.form.get(f'final_pf_{student_id}'), 5)
                    written = clamp_mark(request.form.get(f'final_written_{student_id}'), 80)
                    cursor.execute('''
                        INSERT OR REPLACE INTO marks (student_id, subject, exam_type, pt, ma, se, pf, written)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (student_id, subject, 'Final', pt, ma, se, pf, written))
                    saved_count += 1

        print(f"Saved {saved_count} mark entries")
        conn.commit()
        flash(f'Bulk marks saved for Class {class_name} Section {section} ({subject}, {exam_type})! {saved_count} records updated.', 'success')
        conn.close()
        return redirect(url_for('bulk_marks'))

        conn.commit()
        flash(f'Bulk marks saved for Class {class_name} Section {section} ({subject}, {exam_type})!', 'success')
        conn.close()
        return redirect(url_for('bulk_marks'))
    
    # Get all classes
    cursor.execute('SELECT DISTINCT class_name FROM students ORDER BY class_name')
    classes = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT exam_name, max_marks, subjects, classes, sections FROM custom_exams ORDER BY created_at DESC')
    custom_exams = [dict(row) for row in cursor.fetchall()]

    conn.close()
    
    return render_template('bulk_marks.html', classes=classes, subjects=SUBJECTS, custom_exams=custom_exams)

@app.route('/get-class-students')
def get_class_students():
    """Get students by class and section for AJAX"""
    class_name = request.args.get('class_name')
    section = request.args.get('section')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT admission_no, name, roll_no FROM students WHERE class_name = ? AND section = ? ORDER BY roll_no',
                 (class_name, section))
    students = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in students])

@app.route('/api/get-marks')
def api_get_marks():
    """Get existing marks for a student and subject"""
    student_id = request.args.get('student_id')
    subject = request.args.get('subject')
    exam_type = request.args.get('exam_type')
    
    if not student_id or not subject or not exam_type:
        return jsonify(None)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM marks 
        WHERE student_id = ? AND subject = ? AND exam_type = ?
    ''', (student_id, subject, exam_type))
    mark = cursor.fetchone()
    conn.close()
    
    if mark:
        return jsonify(dict(mark))
    return jsonify(None)

@app.route('/api/custom-exams')
def api_custom_exams():
    """Get custom exams matching selected student and subject"""
    student_id = request.args.get('student_id')
    subject = request.args.get('subject')
    
    if not student_id or not subject:
        return jsonify([])
    
    # Get student details for filtering
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT class_name, section FROM students WHERE admission_no = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify([])
    
    student_class = student['class_name']
    student_section = student['section']
    
    # Get matching custom exams
    cursor.execute('SELECT * FROM custom_exams ORDER BY created_at DESC')
    raw_exams = cursor.fetchall()
    
    import json
    matching_exams = []
    for row in raw_exams:
        exam = dict(row)
        exam_classes = json.loads(exam['classes'] or '[]')
        exam_sections = json.loads(exam['sections'] or '[]')
        exam_subjects = json.loads(exam['subjects'] or '[]')
        
        # Match class, section, subject
        if (student_class in exam_classes and 
            student_section in exam_sections and 
            subject in exam_subjects):
            matching_exams.append({
                'exam_name': exam['exam_name'],
                'max_marks': exam['max_marks']
            })
    
    conn.close()
    return jsonify(matching_exams)
@app.route('/result/<admission_no>')
def result_detail(admission_no):
    """View detailed result for a student"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get student details
    cursor.execute('SELECT * FROM students WHERE admission_no = ?', (admission_no,))
    student = cursor.fetchone()
    
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('index'))
    
    # Get marks
    cursor.execute('SELECT * FROM marks WHERE student_id = ?', (admission_no,))
    marks = cursor.fetchall()
    
    conn.close()
    
    # Calculate result
    result = calculate_result(student, marks)
    
    return render_template('result_card.html', result=result, student=student)

def calculate_result(student, marks):
    """Calculate complete result for a student"""
    subject_results = []
    grand_total = 0
    
    for subject in SUBJECTS:
        # Get Half Yearly marks
        hy_mark = next((m for m in marks if m['subject'] == subject and m['exam_type'] == 'Half Yearly'), None)
        # Get Final marks
        final_mark = next((m for m in marks if m['subject'] == subject and m['exam_type'] == 'Final'), None)
        
        if hy_mark and final_mark:
            # Calculate totals - handle Computer subject differently
            if subject.lower() == 'computer':
                hy_total = calculate_total(0, 0, 0, 0, 0, subject, hy_mark['theory'], hy_mark['practical'])
                final_total = calculate_total(0, 0, 0, 0, 0, subject, final_mark['theory'], final_mark['practical'])
            else:
                hy_total = calculate_total(hy_mark['pt'], hy_mark['ma'], hy_mark['se'], hy_mark['pf'], hy_mark['written'], subject)
                final_total = calculate_total(final_mark['pt'], final_mark['ma'], final_mark['se'], final_mark['pf'], final_mark['written'], subject)
            
            # Calculate weighted score
            weighted_score = calculate_weighted_score(hy_total, final_total)
            
            subject_results.append({
                'subject': subject,
                'hy_pt': hy_mark['pt'],
                'hy_ma': hy_mark['ma'],
                'hy_se': hy_mark['se'],
                'hy_pf': hy_mark['pf'],
                'hy_written': hy_mark['written'],
                'hy_theory': hy_mark['theory'] if subject.lower() == 'computer' else 0,
                'hy_practical': hy_mark['practical'] if subject.lower() == 'computer' else 0,
                'hy_total': hy_total,
                'final_pt': final_mark['pt'],
                'final_ma': final_mark['ma'],
                'final_se': final_mark['se'],
                'final_pf': final_mark['pf'],
                'final_written': final_mark['written'],
                'final_theory': final_mark['theory'] if subject.lower() == 'computer' else 0,
                'final_practical': final_mark['practical'] if subject.lower() == 'computer' else 0,
                'final_total': final_total,
                'weighted_score': round(weighted_score, 2)
            })
            
            grand_total += weighted_score
    
    # Calculate percentage (out of 100 per subject)
    num_subjects = len(subject_results)
    percentage = (grand_total / num_subjects) if num_subjects > 0 else 0
    
    # Assign grade
    grade = assign_grade(percentage)
    
    # Generate remarks
    remarks = get_remarks(grade, percentage)
    
    return {
        'student': dict(student),
        'subjects': subject_results,
        'grand_total': round(grand_total, 2),
        'percentage': round(percentage, 2),
        'grade': grade,
        'remarks': remarks
    }

@app.route('/search')
def search():
    """Search for a student"""
    query = request.args.get('q', '')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM students 
        WHERE name LIKE ? OR admission_no LIKE ? OR class_name LIKE ?
        ORDER BY class_name, name
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    students = cursor.fetchall()
    conn.close()
    
    return render_template('search.html', students=students, query=query)

@app.route('/class-results')
def class_results():
    """View results by class"""
    class_name = request.args.get('class_name', '7')
    section = request.args.get('section', 'A')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get students in the class
    cursor.execute('SELECT * FROM students WHERE class_name = ? AND section = ? ORDER BY roll_no',
                 (class_name, section))
    students = cursor.fetchall()
    
    results_list = []
    for student in students:
        cursor.execute('SELECT * FROM marks WHERE student_id = ?', (student['admission_no'],))
        marks = cursor.fetchall()
        
        if len(marks) >= len(SUBJECTS):
            result = calculate_result(student, marks)
            results_list.append(result)
    
    conn.close()
    return render_template('class_results.html', results=results_list, class_name=class_name, section=section)

@app.route('/export-excel')
def export_excel():
    """Export all results to CSV"""
    import csv
    import io
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY class_name, section, roll_no')
    students = cursor.fetchall()
    
    results_list = []
    for student in students:
        cursor.execute('SELECT * FROM marks WHERE student_id = ?', (student['admission_no'],))
        marks = cursor.fetchall()
        
        if len(marks) >= len(SUBJECTS):
            result = calculate_result(student, marks)
            results_list.append(result)
    
    conn.close()
    
    # Create CSV using csv writer and StringIO for proper escaping
    output_io = io.StringIO()
    writer = csv.writer(output_io)

    writer.writerow(['Admission No', 'Name', 'Class', 'Section', 'Roll No'])
    writer.writerow([])
    writer.writerow(['Subject', 'HY PT', 'HY MA', 'HY SE', 'HY PF', 'HY Written', 'HY Total',
                     'Final PT', 'Final MA', 'Final SE', 'Final PF', 'Final Written', 'Final Total',
                     'Weighted Score'])

    for result in results_list:
        writer.writerow([result['student']['admission_no'], result['student']['name'],
                         result['student']['class_name'], result['student']['section'],
                         result['student']['roll_no']])
        writer.writerow(['Total', '', '', '', '', '', '', '', '', '', '', '',
                         result['grand_total'], result['percentage'], result['grade']])
        writer.writerow([])

    response = make_response(output_io.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=results.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response

@app.route('/create-exam', methods=['GET', 'POST'])
def create_exam():
    """Create a custom exam"""
    if request.method == 'POST':
        exam_name_raw = request.form.get('exam_name')
        if not exam_name_raw:
            flash('Exam name is required.', 'error')
            return redirect(url_for('create_exam'))
        exam_name = exam_name_raw.upper()
        classes = request.form.getlist('classes')
        sections = request.form.getlist('sections')
        subjects = request.form.getlist('subjects')
        students = request.form.getlist('students') if request.form.getlist('students') else None
        max_marks = float(request.form.get('max_marks', 100))
        
        import json
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO custom_exams (exam_name, classes, sections, subjects, students, max_marks)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (exam_name, json.dumps(classes), json.dumps(sections), json.dumps(subjects), 
                  json.dumps(students) if students else None, max_marks))
            conn.commit()
            flash(f'Exam "{exam_name}" created successfully!', 'success')
            return redirect(url_for('exams'))
        except sqlite3.IntegrityError:
            flash('Exam name already exists!', 'error')
        finally:
            conn.close()
    
    # Get available options
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT class_name FROM students ORDER BY class_name')
    available_classes = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT section FROM students ORDER BY section')
    available_sections = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT admission_no, name, class_name, section FROM students ORDER BY class_name, name')
    available_students = cursor.fetchall()
    conn.close()
    
    return render_template('create_exam.html', 
                         available_classes=available_classes,
                         available_sections=available_sections,
                         available_students=available_students,
                         subjects=SUBJECTS)

@app.route('/edit-exam/<exam_name>', methods=['GET', 'POST'])
def edit_exam(exam_name):
    """Edit an existing custom exam"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the exam to edit
    cursor.execute('SELECT * FROM custom_exams WHERE exam_name = ?', (exam_name,))
    exam = cursor.fetchone()
    
    if not exam:
        flash('Exam not found!', 'error')
        conn.close()
        return redirect(url_for('exams'))
    
    if request.method == 'POST':
        exam_name_raw = request.form.get('exam_name')
        if not exam_name_raw:
            flash('Exam name is required.', 'error')
            return redirect(url_for('edit_exam', exam_name=exam_name))
        
        exam_name_new = exam_name_raw.upper()
        classes = request.form.getlist('classes')
        sections = request.form.getlist('sections')
        subjects = request.form.getlist('subjects')
        students = request.form.getlist('students') if request.form.getlist('students') else None
        max_marks = float(request.form.get('max_marks', 100))
        
        import json
        
        try:
            cursor.execute('''
                UPDATE custom_exams 
                SET exam_name = ?, classes = ?, sections = ?, subjects = ?, students = ?, max_marks = ?
                WHERE exam_name = ?
            ''', (exam_name_new, json.dumps(classes), json.dumps(sections), json.dumps(subjects), 
                  json.dumps(students) if students else None, max_marks, exam_name))
            conn.commit()
            flash(f'Exam "{exam_name_new}" updated successfully!', 'success')
            return redirect(url_for('exams'))
        except sqlite3.IntegrityError:
            flash('Exam name already exists!', 'error')
        finally:
            if conn:
                conn.close()
    
    # Parse existing exam config
    import json
    exam_dict = dict(exam)
    exam_dict['classes'] = json.loads(exam['classes']) if exam['classes'] else []
    exam_dict['sections'] = json.loads(exam['sections']) if exam['sections'] else []
    exam_dict['subjects'] = json.loads(exam['subjects']) if exam['subjects'] else []
    exam_dict['students'] = json.loads(exam['students']) if exam['students'] else []
    
    # Get available options
    cursor.execute('SELECT DISTINCT class_name FROM students ORDER BY class_name')
    available_classes = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT section FROM students ORDER BY section')
    available_sections = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT admission_no, name, class_name, section FROM students ORDER BY class_name, name')
    available_students = cursor.fetchall()
    conn.close()
    
    return render_template('edit_exam.html', 
                         exam=exam_dict,
                         available_classes=available_classes,
                         available_sections=available_sections,
                         available_students=available_students,
                         subjects=SUBJECTS)

@app.route('/delete-exam/<exam_name>', methods=['POST'])
def delete_exam(exam_name):
    """Delete a custom exam"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Delete exam and associated marks
        cursor.execute('DELETE FROM marks WHERE exam_type = ?', (exam_name,))
        cursor.execute('DELETE FROM custom_exams WHERE exam_name = ?', (exam_name,))
        conn.commit()
        flash(f'Exam "{exam_name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting exam: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('exams'))

@app.route('/debug-exams')
def debug_exams():
    """Debug endpoint to check exam data"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM custom_exams ORDER BY created_at DESC')
    exams = [dict(row) for row in cursor.fetchall()]
    conn.close()

    import json
    for exam in exams:
        exam['classes'] = json.loads(exam['classes'])
        exam['sections'] = json.loads(exam['sections'])
        exam['subjects'] = json.loads(exam['subjects'])
        if exam.get('students'):
            exam['students'] = json.loads(exam['students'])

    return f"Found {len(exams)} exams: {[e['exam_name'] for e in exams]}"

@app.route('/exams')
def exams():
    """View all custom exams"""
    from datetime import datetime
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM custom_exams ORDER BY created_at DESC')
    exams = [dict(row) for row in cursor.fetchall()]
    conn.close()

    import json
    for exam in exams:
        exam['classes'] = json.loads(exam['classes'])
        exam['sections'] = json.loads(exam['sections'])
        exam['subjects'] = json.loads(exam['subjects'])
        if exam.get('students'):
            exam['students'] = json.loads(exam['students'])
        
        # Convert created_at string to datetime object for strftime
        created_at_str = exam.get('created_at')
        if created_at_str:
            try:
                # Handle both 'YYYY-MM-DD HH:MM:SS' and 'YYYY-MM-DD'
                if len(created_at_str) > 10:
                    exam['created_at'] = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
                else:
                    exam['created_at'] = datetime.strptime(created_at_str, '%Y-%m-%d')
            except ValueError:
                exam['created_at'] = None
        else:
            exam['created_at'] = None

    return render_template('exams.html', exams=exams)

@app.route('/enter-exam-marks/<exam_name>', methods=['GET', 'POST'])
def enter_exam_marks(exam_name):
    """Enter marks for a custom exam"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get exam details
    cursor.execute('SELECT * FROM custom_exams WHERE exam_name = ?', (exam_name,))
    exam = cursor.fetchone()
    
    if not exam:
        flash('Exam not found!', 'error')
        return redirect(url_for('exams'))
    
    import json
    exam_classes = json.loads(exam['classes'])
    exam_sections = json.loads(exam['sections'])
    exam_subjects = json.loads(exam['subjects'])
    exam_students = json.loads(exam['students']) if exam['students'] else None
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject = request.form.get('subject')
        marks = float(request.form.get('marks', 0) or 0)
        
        # Validate marks don't exceed max
        if marks > exam['max_marks']:
            flash(f'Marks cannot exceed {exam["max_marks"]}!', 'error')
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO marks (student_id, subject, exam_type, written)
                VALUES (?, ?, ?, ?)
            ''', (student_id, subject, exam_name, marks))
            conn.commit()
            flash(f'Marks saved for {subject}!', 'success')
    
    # Get eligible students
    if exam_students:
        # Specific students
        placeholders = ','.join('?' * len(exam_students))
        cursor.execute(f'SELECT admission_no, name, class_name, section FROM students WHERE admission_no IN ({placeholders}) ORDER BY name', exam_students)
    else:
        # Filter by class and section
        class_placeholders = ','.join('?' * len(exam_classes))
        section_placeholders = ','.join('?' * len(exam_sections))
        cursor.execute(f'''
            SELECT admission_no, name, class_name, section FROM students 
            WHERE class_name IN ({class_placeholders}) AND section IN ({section_placeholders})
            ORDER BY class_name, section, name
        ''', exam_classes + exam_sections)
    
    students = cursor.fetchall()
    conn.close()
    
    return render_template('enter_exam_marks.html', 
                         exam=exam, 
                         students=students, 
                         subjects=exam_subjects,
                         exam_name=exam_name)

@app.route('/exam-results/<exam_name>')
def exam_results(exam_name):
    """View results for a custom exam"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get exam details
    cursor.execute('SELECT * FROM custom_exams WHERE exam_name = ?', (exam_name,))
    exam = cursor.fetchone()
    
    if not exam:
        flash('Exam not found!', 'error')
        return redirect(url_for('exams'))
    
    import json
    exam_classes = json.loads(exam['classes'])
    exam_sections = json.loads(exam['sections'])
    exam_subjects = json.loads(exam['subjects'])
    exam_students = json.loads(exam['students']) if exam['students'] else None
    
    # Get results
    results = []
    if exam_students:
        placeholders = ','.join('?' * len(exam_students))
        cursor.execute(f'SELECT * FROM students WHERE admission_no IN ({placeholders}) ORDER BY name', exam_students)
    else:
        class_placeholders = ','.join('?' * len(exam_classes))
        section_placeholders = ','.join('?' * len(exam_sections))
        cursor.execute(f'''
            SELECT * FROM students 
            WHERE class_name IN ({class_placeholders}) AND section IN ({section_placeholders})
            ORDER BY class_name, section, name
        ''', exam_classes + exam_sections)
    
    students = cursor.fetchall()
    
    for student in students:
        student_marks = {}
        total_marks = 0
        subjects_taken = 0
        
        for subject in exam_subjects:
            cursor.execute('SELECT written FROM marks WHERE student_id = ? AND subject = ? AND exam_type = ?',
                         (student['admission_no'], subject, exam_name))
            mark = cursor.fetchone()
            if mark:
                student_marks[subject] = mark[0]
                total_marks += mark[0]
                subjects_taken += 1
            else:
                student_marks[subject] = 0
        
        if subjects_taken > 0:
            percentage = (total_marks / (subjects_taken * exam['max_marks'])) * 100
            results.append({
                'student': dict(student),
                'marks': student_marks,
                'total': total_marks,
                'percentage': round(percentage, 2),
                'subjects_taken': subjects_taken
            })
    
    conn.close()
    
    return render_template('exam_results.html', 
                         exam=dict(exam), 
                         results=results, 
                         subjects=exam_subjects,
                         exam_name=exam_name)

@app.route('/pt2-results')
def pt2_results():
    """Dedicated PT2 results for Class 7A"""
    return exam_results('PT2')

@app.route('/half-yearly-results')
def half_yearly_results():
    """Detailed Half Yearly Marksheet"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY class_name, section, roll_no')
    students = cursor.fetchall()
    
    grouped_results = []
    SUBJECTS = ['English', 'Hindi', 'Maths', 'Science', 'SST', 'Computer', 'French']
    
    for student in students:
        cursor.execute("SELECT subject, pt, ma, se, pf, written FROM marks WHERE student_id = ? AND exam_type = 'Half Yearly'", (student['admission_no'],))
        marks_raw = cursor.fetchall()
        student_marks = {row['subject']: dict(row) for row in marks_raw}
        
        grouped_results.append({
            'student': dict(student),
            'marks': student_marks,
            'subjects': SUBJECTS
        })
    
    conn.close()
    return render_template('half_yearly_detailed.html', grouped_results=grouped_results, subjects=SUBJECTS)

@app.route('/final-result')
def final_result():
    """Detailed Final Exam Marksheet"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY class_name, section, roll_no')
    students = cursor.fetchall()
    
    grouped_results = []
    SUBJECTS = ['English', 'Hindi', 'Maths', 'Science', 'SST', 'Computer', 'French']
    
    for student in students:
        cursor.execute("SELECT subject, pt, ma, se, pf, written FROM marks WHERE student_id = ? AND exam_type = 'Final'", (student['admission_no'],))
        marks_raw = cursor.fetchall()
        student_marks = {row['subject']: dict(row) for row in marks_raw}
        
        grouped_results.append({
            'student': dict(student),
            'marks': student_marks,
            'subjects': SUBJECTS
        })
    
    conn.close()
    return render_template('final_result.html', grouped_results=grouped_results, subjects=SUBJECTS)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error'), 500

# Print all routes for debugging
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    debug_mode = True  # Force debug mode
    app.run(debug=debug_mode, port=int(os.getenv('PORT', 5000)))  # For production use Gunicorn or another WSGI server
