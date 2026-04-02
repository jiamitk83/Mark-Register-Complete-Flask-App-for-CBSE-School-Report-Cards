# Bulk Marks Fix - Progress Tracker

## Steps (0/4 Complete)

### 1. [x] Create TODO file ✓
### 2. [x] Fix bulk_marks route - inline saves with logging ✓  
### 3. [x] Add logging/error handling ✓
### 4. [ ] Test bulk submission → attempt_completion

**Bug**: save_computer/save_regular defined but never called  
**Fix**: Add if subject=='computer': save_computer else save_regular in student loop
