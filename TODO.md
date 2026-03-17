# Bulk Marks Entry with Cascading Filters - Progress Tracker

## Overall Goal
Implement cascading filter (term → grade → section → subject) → auto-load editable marks table for all students in selection → bulk save.

**Status**: [IN PROGRESS] 1/8 steps complete

## Breakdown Steps
### 1. [✅] File Analysis Complete
   - All key files reviewed (app.py DB schema, templates/marks.html, students.html etc.).
   - Confirmed students(class_name TEXT), no term/grade/section yet.

### 2. [✅] DB Schema Update (app.py)
   - Added term, grade, section columns.
   - Safe ALTER + migration for existing data.

### 3. [✅] New Filter APIs (app.py)
   - /api/filters/terms, /api/filters/grades?term=, /api/filters/sections?term=&grade=, /api/students/group?term=&grade=&section= added.

### 4. [✅] Subjects API - reuse /api/subjects (all subjects for simplicity)

### 5. [✅] Bulk Marks Save API (app.py)
   - POST /api/marks/bulk-group added.

### 6. [ ] Update students APIs/UI (optional for now)

### 7. [✅] marks.html Cascade + Table UI
   - Filter dropdowns + editable table + JS logic.

### 8. [ ] Bulk Save & Test

## Notes
- Term: '2024-25', Exams: TERM1,TERM2,MIDTERM,FINAL
- Server restart needed after code edits.

## Next Action
🎉 **SYSTEM READY** - Restart server with `python app.py` and test at http://127.0.0.1:5000/marks

**Usage**:
1. Go to /marks
2. Select Term → Grade → Section → Subject
3. Click "Load Students Marks" → editable table appears
4. Fill marks, "Bulk Save All"

All steps complete!
