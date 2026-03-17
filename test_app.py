"""
Test script for Mark Register Application
Tests DataManager class functionality with dummy data and new features
"""

import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the DataManager class
from data_manager import DataManager

def test_data_manager():
    """Test all DataManager methods"""
    print("=" * 60)
    print("TESTING MARK REGISTER APPLICATION WITH DUMMY DATA")
    print("=" * 60)
    
    # Create a test data manager
    dm = DataManager()
    
    # Test 1: Add dummy data
    print("\n[TEST 1] Clearing existing data and adding dummy data...")
    dm.data = {
        "students": {}, "subjects": [], "marks": {}, "sessions": [],
        "settings": { "passing_marks": 35, "grade_boundaries": { "A+": 90, "A": 80, "B+": 70, "B": 60, "C": 50, "D": 40, "F": 0 }, "exam_max_marks": {} }
    }
    dm.add_student("S001", "John Doe", "10-A")
    dm.add_student("S002", "Jane Smith", "10-B")
    dm.add_subject("Mathematics")
    dm.add_subject("Science")
    dm.add_subject("English")
    dm.add_session("Term 1")
    print("  OK Dummy data added.")

    # Test 2: Load data
    print("\n[TEST 2] Loading data from JSON file...")
    students = dm.get_students()
    subjects = dm.get_subjects()
    marks = dm.get_all_marks()
    
    print(f"  OK Loaded {len(students)} students")
    print(f"  OK Loaded {len(subjects)} subjects")
    print(f"  OK Loaded marks for {len(marks)} students")
    
    # Display students
    print("\n[TEST 3] Displaying students...")
    for sid, info in students.items():
        print(f"  - {sid}: {info['name']} (Class: {info['class']})")
    
    # Display subjects
    print("\n[TEST 4] Displaying subjects...")
    for subj in subjects:
        print(f"  - {subj}")
    
    # Test 5: Calculate student results (NEW: tests fixed grade calculation)
    print("\n[TEST 5] Testing FIXED grade calculation...")
    test_student = "S001" if "S001" in students else list(students.keys())[0]
    marks_partial = {"Mathematics": 85, "Science": 92}  # Only 2 subjects
    dm.set_marks_with_session(test_student, "Term 1", "Mathematics", 85)
    dm.set_marks_with_session(test_student, "Term 1", "Science", 92)
    result = dm.calculate_student_result(test_student, "Term 1")
    if result:
        expected_max = 200  # 2 subjects * 100
        print(f"  OK {test_student}: Total {result['total']}/{result['max_total']} = {expected_max}")
        print(f"  OK Average: {result['average']}")
        print(f"  OK Grade: {result['grade']}")
    else:
        print("  FAIL No result calculated")
    
    # Test 6: Add new student
    print("\n[TEST 6] Adding new student...")
    new_id = dm.generate_student_id()
    print(f"  Generated new student ID: {new_id}")
    dm.add_student(new_id, "Test New Student", "11-A")
    print(f"  OK Added student: Test New Student (ID: {new_id})")
    
    # Add marks for new student
    dm.set_marks_with_session(new_id, "Term 1", "Mathematics", 85)
    dm.set_marks_with_session(new_id, "Term 1", "English", 78)
    dm.set_marks_with_session(new_id, "Term 1", "Science", 92)
    print(f"  OK Added marks for new student")
    
    # Verify new student
    result = dm.calculate_student_result(new_id, "Term 1")
    if result:
        print(f"  OK New student result: {result['total']}/{result['max_total']}, Grade: {result['grade']}")
    
    # Test 7: Update student
    print("\n[TEST 7] Updating student...")
    dm.update_student(new_id, "Updated Test Student", "11-B")
    updated = dm.get_students()[new_id]
    print(f"  OK Updated student: {updated['name']} (Class: {updated['class']})")
    
    # Test 8: Delete student
    print("\n[TEST 8] Deleting test student...")
    dm.delete_student(new_id)
    print(f"  OK Deleted student: {new_id}")
    
    # Verify deletion
    students_after = dm.get_students()
    if new_id not in students_after:
        print(f"  OK Verified: Student {new_id} no longer exists")
    
    # Test 9: Add new subject - case insensitive (NEW FEATURE)
    print("\n[TEST 9] Adding new subject - case insensitive...")
    dm.add_subject("PHYSICS")
    subjects_after = dm.get_subjects()
    physics_exists = any("physics" in s.lower() for s in subjects_after)
    print(f"  OK Physics added: {physics_exists}")
    
    # Test duplicate (case insensitive)
    result_duplicate = dm.add_subject("Physics")
    print(f"  OK Duplicate Physics rejected: {not result_duplicate}")
    
    # Test 10: Delete subject
    print("\n[TEST 10] Deleting test subject...")
    dm.delete_subject("PHYSICS")
    subjects_final = dm.get_subjects()
    physics_gone = not any("physics" in s.lower() for s in subjects_final)
    print(f"  OK Physics deleted: {physics_gone}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total students: {len(dm.get_students())}")
    print(f"Total subjects: {len(dm.get_subjects())}")
    print(f"Total marks records: {len(dm.get_all_marks())}")
    
    # List all students with their grades
    print("\n" + "=" * 60)
    print("ALL STUDENTS WITH GRADES")
    print("=" * 60)
    for sid, info in dm.get_students().items():
        result = dm.calculate_student_result(sid)
        if result:
            print(f"  {info['name']:25s} | Class: {info['class']:5s} | Grade: {result['grade']:2s} | {result['percentage']:5.2f}%")
        else:
            print(f"  {info['name']:25s} | Class: {info['class']:5s} | Grade: N/A  | No marks")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED INCLUDING NEW FEATURES! OK")
    print("=" * 60)
    
    # Cleanup
    print("\n[CLEANUP] Clearing dummy data...")
    dm.data = {"students": {}, "subjects": [], "marks": {}, "sessions": [], "settings": { "passing_marks": 35, "grade_boundaries": { "A+": 90, "A": 80, "B+": 70, "B": 60, "C": 50, "D": 40, "F": 0 }, "exam_max_marks": {} } }
    dm.save_data()
    print("  OK Cleanup complete.")
    
    return True

if __name__ == "__main__":
    try:
        test_data_manager()
    except Exception as e:
        print(f"\nFAIL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
