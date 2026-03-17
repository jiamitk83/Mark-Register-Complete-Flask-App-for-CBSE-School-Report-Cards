# Custom Max Marks Editor (Settings UI)

## 🎯 Goal
**Web UI** in Settings page to edit **per-exam per-subject max marks** matrix.

## 📋 Current State
```
exam_max_marks table exists ✅
marks.html shows max_marks (read-only) ✅
No edit UI
```

## 🛠️ Implementation Plan

**1. templates/settings.html** - Add new card:
```
📊 Exam Max Marks Editor
┌─ Subjects ─┐  TERM1  TERM2  MIDTERM  FINAL
│ Math      │  [50]   [50]   [70]    [100]
│ Science   │  [50]   [50]   [70]    [100]
└───────────┘  Save All
```

**2. app.py** - API endpoints:
```
GET /api/maxmarks → {subjects: [{id, name, TERM1:50, TERM2:50, ...}]}
POST /api/maxmarks → Save matrix
```

**3. JS** (settings.html):
```
Load matrix → Edit inputs → Batch save
```

## 📁 Files to Edit
```
[ ] templates/settings.html - Matrix editor UI
[ ] app.py - /api/maxmarks GET/POST endpoints
```

## ✅ Features After Completion
- Click Settings → Edit any exam/subject max marks
- Marks entry shows **your custom max marks**
- Results use **custom max marks** for % calculation
- Bulk update all at once

**Ready to implement!**
