# 4 Exams Per Year + Per-Exam Max Marks Feature

## 🎯 Goal
Support 4 examinations (Term1, Term2, MidTerm, Final) with **different max marks per subject per exam**.

## 📊 Current State
- Marks table: `exam_type TEXT DEFAULT 'terminal'` (single field)
- Results: assumes **100 max marks** per subject
- No exam selector in marks.html
- No per-exam max marks storage

## 🛠️ Plan (File Level)

**1. Database Changes (app.py init_db):**
```
exam_max_marks table:
- id, exam_type, subject_id, max_marks
Default: Term1/Term2=50, MidTerm=70, Final=100 per subject
```

**2. Marks Entry (templates/marks.html):**
- Add **Exam dropdown** (4 options)
- Show **max marks** for selected exam/subject
- Save `exam_type` with marks

**3. API Endpoints (app.py):**
```
GET /api/exams - List 4 exams
GET /api/maxmarks?exam=Term1&subject=Math - Get max marks
POST /api/maxmarks - Update max marks
```

**4. Results Calculation (app.py results):**
```
Use exam_max_marks table for accurate %/grades per exam
Separate results by exam_type
```

**5. Settings (templates/settings.html):**
```
Exam Max Marks matrix editor (4 exams × subjects)
```

## 📁 Files to Edit
```
[ ] app.py - DB table, APIs, results logic
[ ] templates/marks.html - Exam selector + max marks display
[ ] templates/results.html - Per-exam results
[ ] templates/settings.html - Max marks editor
```

## ✅ Prerequisites
```
[ ] Confirm 4 exam names? (Term1, Term2, MidTerm, Final?)
[ ] Any existing marks data to preserve?
```

**✅ Plan Approved - OK to proceed**
