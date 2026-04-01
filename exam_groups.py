#!/usr/bin/env python3
\"\"\"Exam Group Management - HALF YEARLY as PT1 + Components\"\"\"

import sqlite3
from typing import List, Dict, Any
import json

class ExamGroupManager:
    def __init__(self, db_path='school_report.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS exam_groups (
                id INTEGER PRIMARY KEY,
                group_name TEXT UNIQUE NOT NULL,
                description TEXT,
                component_exams TEXT,  -- JSON list of exam_names
                weightings TEXT,       -- JSON dict exam_name:weight (e.g., {'PT1':0.2})
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_group(self, group_name: str, exams: List[str], weightings: Dict[str, float] = None) -> bool:
        if not weightings:
            weightings = {exam: 1.0/len(exams) for exam in exams}
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO exam_groups (group_name, component_exams, weightings)
                VALUES (?, ?, ?)
            ''', (group_name, json.dumps(exams), json.dumps(weightings)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_group(self, group_name: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM exam_groups WHERE group_name = ?', (group_name,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'group_name': row[1],
                'description': row[2],
                'exams': json.loads(row[3]),
                'weightings': json.loads(row[4])
            }
        return None
    
    def list_groups(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM exam_groups')
        rows = c.fetchall()
        conn.close()
        return [{
            'id': r[0], 'group_name': r[1], 'description': r[2],
            'exams': json.loads(r[3]), 'weightings': json.loads(r[4])
        } for r in rows]
    
    def calculate_group_score(self, student_id: str, subject: str, group_name: str) -> Optional[float]:
        group = self.get_group(group_name)
        if not group:
            return None
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        total_weighted = 0.0
        for exam_name, weight in group['weightings'].items():
            c.execute('''
                SELECT written FROM marks 
                WHERE student_id=? AND subject=? AND exam_type=?
            ''', (student_id, subject, exam_name))
            row = c.fetchone()
            score = row[0] if row else 0
            total_weighted += score * weight
        
        conn.close()
        return total_weighted

# USAGE EXAMPLE
if __name__ == "__main__":
    manager = ExamGroupManager()
    
    # Create HALF YEARLY group: PT1(20%) + MA(15%) + SE(15%) + PF(15%) + HY(35%)
    exams = ["PT1", "MA", "SE", "PF", "HY"]
    weightings = {"PT1": 0.2, "MA": 0.15, "SE": 0.15, "PF": 0.15, "HY": 0.35}
    
    if manager.create_group("HALF YEARLY", exams, weightings):
        print("✅ HALF YEARLY group created!")
    
    print("Groups:", manager.list_groups())
    
    # Calculate score
    score = manager.calculate_group_score("ADM001", "English", "HALF YEARLY")
    print(f"HALF YEARLY score for ADM001 English: {score}")
    
    print("\\nIntegration with Flask app.py:")
    print("1. Add ExamGroupManager to app.py")
    print("2. /create-group POST → manager.create_group()") 
    print("3. /results → Use manager.calculate_group_score()")
    print("4. UI: Group dropdown in enter-marks → auto-populate components")
