import sqlite3
import csv
import os

DB = 'mark_register.db'

def bulk_add_students(csv_file):
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # Get next student ID
    cursor.execute("SELECT COALESCE(MAX(CAST(SUBSTR(student_id, 2) AS INTEGER)), 0) + 1 FROM students WHERE student_id LIKE 'S%'")
    next_num = cursor.fetchone()[0]
    
    added = 0
    skipped = 0
    
    print(f"📊 Importing from {csv_file}...")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, 1):
                if len(row) < 2 or not row[0].strip():
                    skipped += 1
                    continue
                
                name = row[0].strip().title()
                class_name = row[1].strip().title()
                
                if len(name) < 2:
                    skipped += 1
                    continue
                
                student_id = f"S{next_num:03d}"
                try:
                    cursor.execute(
                        "INSERT INTO students (student_id, name, class_name) VALUES (?, ?, ?)",
                        (student_id, name, class_name)
                    )
                    print(f"✅ {student_id}: {name} ({class_name})")
                    next_num += 1
                    added += 1
                except sqlite3.IntegrityError:
                    print(f"⚠️  {student_id} already exists (skipped)")
                    skipped += 1
        
        conn.commit()
        print(f"\n🎉 Complete! Added: {added}, Skipped: {skipped}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    csv_file = input("📁 Enter CSV file path (name,class format): ").strip().strip('"\'')
    bulk_add_students(csv_file)

