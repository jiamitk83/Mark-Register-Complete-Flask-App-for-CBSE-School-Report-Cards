#!/usr/bin/env python3
\"\"\"Hierarchical Exam System: Main Exam → Sub-Exams\"\"\"

import sqlite3
import json
from typing import List, Dict, Optional

class HierarchicalExamManager:
    def __init__(self, db_path='school_report.db'):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Main Exams (Half Yearly, Final, etc.)
        c.execute('''
            CREATE TABLE IF NOT EXISTS main_exams (
                id INTEGER PRIMARY KEY,
                exam_name TEXT UNIQUE NOT NULL,
                description TEXT,
                total_weight REAL DEFAULT 100.0
            )
        ''')
        
        # Sub-Exams under main exam
        c.execute('''
            CREATE TABLE IF NOT EXISTS sub_exams (
                id INTEGER PRIMARY KEY,
                main_exam_id INTEGER,
                sub_exam_name TEXT,
                max_marks REAL,
                weight REAL,  -- % contribution to main exam
                FOREIGN KEY(main_exam_id) REFERENCES main_exams(id),
                UNIQUE(main_exam_id, sub_exam_name)
            )
        ''')
        
        # Pre-populate common structure
        c.execute('INSERT OR IGNORE INTO main_exams (exam_name, description, total_weight) VALUES (?, ?, ?)', 
                 ('HALF YEARLY', 'Main Half Yearly (PT1 components + written)', 100.0))
        c.execute('INSERT OR IGNORE INTO main_exams (exam_name, description, total_weight) VALUES (?, ?, ?)', 
                 ('FINAL EXAM', 'Main Final Exam (PT2 components + written)', 100.0))
        
        conn.commit()
        conn.close()
    
    def create_main_exam(self, exam_name: str, description: str = '') -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO main_exams (exam_name, description) VALUES (?, ?)', (exam_name, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def add_sub_exam(self, main_exam_name: str, sub_name: str, max_marks: float, weight: float) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            # Get main_exam_id
            c.execute('SELECT id FROM main_exams WHERE exam_name = ?', (main_exam_name,))
            main_id = c.fetchone()
            if not main_id:
                conn.close()
                return False
            
            c.execute('''
                INSERT INTO sub_exams (main_exam_id, sub_exam_name, max_marks, weight)
                VALUES (?, ?, ?, ?)
            ''', (main_id[0], sub_name, max_marks, weight))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_exam_hierarchy(self, main_exam_name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM main_exams WHERE exam_name = ?', (main_exam_name,))
        main = c.fetchone()
        if not main:
            conn.close()
            return None
        
        c.execute('SELECT * FROM sub_exams WHERE main_exam_id = ?', (main[0],))
        subs = c.fetchall()
        
        hierarchy = {
            'main_exam': main[1],
            'description': main[2],
            'total_weight': main[3],
            'sub_exams': []
        }
        
        for sub in subs:
            hierarchy['sub_exams'].append({
                'name': sub[2],
                'max_marks': sub[3],
                'weight': sub[4]
            })
        
        conn.close()
        return hierarchy
    
    def list_main_exams(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT exam_name FROM main_exams')
        names = [row[0] for row in c.fetchall()]
        conn.close()
        return names
    
    def calculate_main_exam_score(self, student_id: str, subject: str, main_exam_name: str) -> Optional[float]:
        hierarchy = self.get_exam_hierarchy(main_exam_name)
        if not hierarchy:
            return None
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        total_score = 0.0
        
        for sub in hierarchy['sub_exams']:
            c.execute('''
                SELECT written FROM marks 
                WHERE student_id=? AND subject=? AND exam_type=?
            ''', (student_id, subject, sub['name']))
            row = c.fetchone()
            score = row[0] if row else 0
            total_score += (score / sub['max_marks']) * sub['weight']
        
        conn.close()
        return total_score

# USAGE: Create HALF YEARLY hierarchy
if __name__ == "__main__":
    mgr = HierarchicalExamManager()
    
    # Create main exam
    mgr.create_main_exam('HALF YEARLY')
    
    # Add sub-exams under HALF YEARLY
    sub_exams = [
        ('PT1', 100, 20),   # PT1 contributes 20%
        ('MA', 5, 15),
        ('SE', 5, 15),
        ('PF', 5, 15),
        ('HY', 80, 35)
    ]
    
    for sub_name, max_marks, weight in sub_exams:
        mgr.add_sub_exam('HALF YEARLY', sub_name, max_marks, weight)
    
    print("HALF YEARLY Hierarchy:")
    print(json.dumps(mgr.get_exam_hierarchy('HALF YEARLY'), indent=2))
    
    # Calculate weighted score
    score = mgr.calculate_main_exam_score('ADM001', 'English', 'HALF YEARLY')
    print(f"HALF YEARLY Score ADM001 English: {score}")
    
    print("\n✅ Ready for Flask integration!")
    print("Add to app.py: mgr = HierarchicalExamManager()")
    print("/edit-exam/HALF YEARLY → shows sub-exams")
    print("/enter-marks → select HALF YEARLY → loads ALL sub-components")
