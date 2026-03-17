import json
import os

DATA_FILE = "mark_register_data.json"

class DataManager:
    """Handles data persistence"""
    
    def __init__(self):
        self.data = {
            "students": {},
            "subjects": [],
            "marks": {},
            "sessions": [],
            "settings": {
                "passing_marks": 35,
                "grade_boundaries": {
                    "A+": 90,
                    "A": 80,
                    "B+": 70,
                    "B": 60,
                    "C": 50,
                    "D": 40,
                    "F": 0
                },
                "exam_max_marks": {}
            }
        }
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Student methods
    def add_student(self, student_id, name, class_name):
        self.data["students"][student_id] = {
            "name": name,
            "class": class_name
        }
        self.save_data()
    
    def update_student(self, student_id, name, class_name):
        if student_id in self.data["students"]:
            self.data["students"][student_id]["name"] = name
            self.data["students"][student_id]["class"] = class_name
            self.save_data()
    
    def delete_student(self, student_id):
        if student_id in self.data["students"]:
            del self.data["students"][student_id]
            if student_id in self.data["marks"]:
                del self.data["marks"][student_id]
            self.save_data()
    
    def get_students(self):
        return self.data["students"]
    
    def generate_student_id(self):
        """Generate a unique student ID automatically"""
        existing_ids = list(self.data["students"].keys())
        if not existing_ids:
            return "S001"
        
        # Extract numeric parts and find the max
        numeric_ids = []
        for sid in existing_ids:
            # Extract number from ID (e.g., "S001" -> 1)
            try:
                num = int(''.join(filter(str.isdigit, sid)))
                numeric_ids.append(num)
            except:
                continue
        
        if numeric_ids:
            new_num = max(numeric_ids) + 1
            return f"S{new_num:03d}"  # S001, S002, etc.
        return "S001"
    
    # Subject methods
    def add_subject(self, subject_name, max_marks=100):
        normalized = subject_name.lower().strip()
        if any(s.lower() == normalized for s in self.data["subjects"]):
            return False
        self.data["subjects"].append(subject_name)
        self.save_data()
        return True
    
    def delete_subject(self, subject_name):
        if subject_name in self.data["subjects"]:
            self.data["subjects"].remove(subject_name)
            # Remove marks for this subject
            for student_id in self.data["marks"]:
                if subject_name in self.data["marks"][student_id]:
                    del self.data["marks"][student_id][subject_name]
            self.save_data()
    
    def get_classes(self):
        """Get unique classes from students"""
        if not self.data["students"]:
            return []
        return sorted(set(info["class"] for info in self.data["students"].values()))

    def get_students_by_class(self, class_name):
        """Get students filtered by class"""
        return {sid: info for sid, info in self.data["students"].items() if info["class"] == class_name}
    
    def get_subjects(self):
        return self.data["subjects"]
    
    # Marks methods
    def get_all_marks(self):
        return self.data["marks"]
    
    # Session methods
    def add_session(self, session_name):
        """Add a new exam session (e.g., Term 1, Term 2, etc.)"""
        if session_name not in self.data["sessions"]:
            self.data["sessions"].append(session_name)
            self.save_data()
    
    def delete_session(self, session_name):
        """Delete a session and its marks"""
        if session_name in self.data["sessions"]:
            self.data["sessions"].remove(session_name)
            # Remove marks for this session
            for student_id in self.data["marks"]:
                if session_name in self.data["marks"][student_id]:
                    del self.data["marks"][student_id][session_name]
            self.save_data()
    
    def get_sessions(self):
        """Get all sessions"""
        return self.data["sessions"]
    
    # Settings methods
    def set_passing_marks(self, passing_marks):
        """Set the minimum passing marks (percentage)"""
        self.data["settings"]["passing_marks"] = passing_marks
        self.save_data()
    
    def get_passing_marks(self):
        """Get the passing marks"""
        return self.data["settings"].get("passing_marks", 35)
    
    def set_grade_boundaries(self, boundaries):
        """Set grade boundaries (dict with grade as key and min percentage as value)"""
        self.data["settings"]["grade_boundaries"] = boundaries
        self.save_data()
    
    def get_grade_boundaries(self):
        """Get grade boundaries"""
        return self.data["settings"].get("grade_boundaries", {
            "A+": 90, "A": 80, "B+": 70, "B": 60, "C": 50, "D": 40, "F": 0
        })
    
    def set_exam_max_marks(self, subject, exam, max_marks):
        """Set max marks for a specific subject exam"""
        key = f"{subject}_{exam}"
        self.data["settings"]["exam_max_marks"][key] = max_marks
        self.save_data()
    
    def get_exam_max_marks(self, subject, exam):
        """Get max marks for a specific subject exam"""
        key = f"{subject}_{exam}"
        return self.data["settings"]["exam_max_marks"].get(key, 100)
    
    def set_marks_with_session(self, student_id, session, subject, marks):
        """Set marks for a student in a specific session"""
        if student_id not in self.data["marks"]:
            self.data["marks"][student_id] = {}
        if session not in self.data["marks"][student_id]:
            self.data["marks"][student_id][session] = {}
        self.data["marks"][student_id][session][subject] = marks
        self.save_data()
    
    def get_marks_with_session(self, student_id, session):
        """Get marks for a student in a specific session"""
        if student_id in self.data["marks"]:
            if session in self.data["marks"][student_id]:
                return self.data["marks"][student_id][session]
        return {}
    
    def get_all_marks_by_session(self, session):
        """Get all marks for a specific session"""
        result = {}
        for student_id, sessions in self.data["marks"].items():
            if session in sessions:
                result[student_id] = sessions[session]
        return result
    
    def calculate_student_result(self, student_id, session=None):
        """Calculate total, average, percentage and grade for a student"""
        marks_by_subject = {}
        max_marks_by_subject = {}
        
        if session:
            # Get marks for a specific session
            marks = self.get_marks_with_session(student_id, session)
            # Get max marks for each subject in this session
            for subject in marks:
                max_marks_by_subject[subject] = self.get_exam_max_marks(subject, session)
        else:
            # Get marks from all sessions combined
            marks = {}
            if student_id in self.data["marks"]:
                for sess, sess_marks in self.data["marks"][student_id].items():
                    if isinstance(sess_marks, dict):
                        for subject, mark in sess_marks.items():
                            if subject not in marks_by_subject:
                                marks_by_subject[subject] = mark
                                max_marks_by_subject[subject] = self.get_exam_max_marks(subject, sess)
            marks = marks_by_subject
        
        if not marks:
            return None
        
        subjects = self.get_subjects()
        grade_boundaries = self.get_grade_boundaries()
        passing_marks = self.get_passing_marks()
        
        # Calculate total marks earned
        total_marks = sum(marks.values())
        
        # Calculate max total based on configured max marks per subject
        max_total = sum(max_marks_by_subject.values()) if max_marks_by_subject else len(marks) * 100
        
        average = total_marks / len(marks) if marks else 0
        percentage = (total_marks / max_total) * 100 if max_total > 0 else 0
        
        # Grade calculation using configurable boundaries
        grade = 'F'
        for g, min_pct in sorted(grade_boundaries.items(), key=lambda x: x[1], reverse=True):
            if percentage >= min_pct:
                grade = g
                break
        
        # Determine pass/fail
        is_pass = percentage >= passing_marks
        
        return {
            "total": round(total_marks, 2),
            "max_total": max_total,
            "average": round(average, 2),
            "percentage": round(percentage, 2),
            "grade": grade,
            "is_pass": is_pass,
            "passing_marks": passing_marks,
            "marks": marks
        }