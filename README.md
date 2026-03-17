# School Mark Register Software

A comprehensive desktop application for managing student marks, subjects, and grades in schools.

## Features

### 1. Student Management
- Add, edit, and delete students
- Store student ID, name, and class information

### 2. Subject Management
- Add and delete subjects
- Flexible subject handling

### 3. Marks Entry
- Enter marks for each student in each subject
- Marks validation (0-100 range)
- Real-time updates

### 4. Results & Reports
- Automatic calculation of:
  - Total marks
  - Average marks
  - Percentage
  - Grade (A+, A, B+, B, C, D, F)
- Generate comprehensive result reports
- Export results to text file

### 5. Data Management
- Automatic data persistence (JSON format)
- Export/backup data functionality

## Requirements

- Python 3.x
- tkinter (included with Python)

## Installation

1. Make sure Python 3 is installed on your computer
2. No additional packages required - tkinter comes with Python

## How to Run

```bash
python mark_register.py
```

## How to Use

### Step 1: Add Subjects
1. Go to the **Subjects** tab
2. Click **Add Subject**
3. Enter subject name (e.g., Mathematics, English, Science)
4. Repeat for all required subjects

### Step 2: Add Students
1. Go to the **Students** tab
2. Click **Add Student**
3. Enter:
   - Student ID (unique identifier)
   - Student Name
   - Class (e.g., 10-A, 11-B)
4. Repeat for all students

### Step 3: Enter Marks
1. Go to the **Marks Entry** tab
2. Select a student from the dropdown
3. Enter marks (0-100) for each subject
4. Click **Save Marks**
5. Repeat for all students

### Step 4: View Results
1. Go to the **Results** tab
2. Click **Generate All Results** to see all student results
3. Click **Export to Text** to save results as a file

## Grade System

| Percentage | Grade |
|-----------|-------|
| 90-100%   | A+    |
| 80-89%    | A     |
| 70-79%    | B+    |
| 60-69%    | B     |
| 50-59%    | C     |
| 40-49%    | D     |
| Below 40% | F     |

## Data Storage

All data is automatically saved to `mark_register_data.json` in the same folder as the application. 

To backup your data:
- Go to **File → Export Data**

## License

Free to use and modify.
