import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data_manager import DataManager


class AddStudentsModule:
    """Standalone Add Students module for Mark Register App"""

    def __init__(self, parent_window=None):
        self.root = tk.Toplevel(parent_window) if parent_window else tk.Tk()
        self.root.title("Add Students - Mark Register")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.configure(bg='#F5F6FA')

        self.data_manager = DataManager()

        self.setup_ui()

        if parent_window:
            self.root.transient(parent_window)
            self.root.grab_set()

    def setup_ui(self):
        """Create professional UI for adding students"""

        # Header
        header_frame = tk.Frame(self.root, bg='#2C3E50', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="👥 Add Students",
            bg='#2C3E50',
            fg='white',
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=20)

        # Main form
        form_frame = tk.LabelFrame(
            self.root,
            text="Student Details",
            font=('Segoe UI', 12, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50',
            padx=20,
            pady=15
        )
        form_frame.pack(fill='both', expand=True, padx=25, pady=15)

        # Student ID
        id_frame = tk.Frame(form_frame, bg='#FFFFFF')
        id_frame.pack(fill='x', pady=10)

        tk.Label(
            id_frame,
            text="Student ID:",
            bg='#FFFFFF',
            fg='#2C3E50',
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w')

        self.id_label = tk.Label(
            id_frame,
            text="",
            bg='#ECF0F1',
            fg='#27AE60',
            font=('Segoe UI', 11),
            relief='solid',
            bd=1,
            padx=10,
            pady=5
        )
        self.id_label.pack(anchor='w', pady=(5, 0))

        # Name
        name_frame = tk.Frame(form_frame, bg='#FFFFFF')
        name_frame.pack(fill='x', pady=10)

        tk.Label(
            name_frame,
            text="Student Name *:",
            bg='#FFFFFF',
            fg='#2C3E50',
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w')

        self.name_entry = ttk.Entry(name_frame, font=('Segoe UI', 11))
        self.name_entry.pack(fill='x', pady=(5, 0))
        self.name_entry.focus()

        # Class
        class_frame = tk.Frame(form_frame, bg='#FFFFFF')
        class_frame.pack(fill='x', pady=10)

        tk.Label(
            class_frame,
            text="Class / Section *:",
            bg='#FFFFFF',
            fg='#2C3E50',
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w')

        self.class_entry = ttk.Entry(class_frame, font=('Segoe UI', 11))
        self.class_entry.pack(fill='x', pady=(5, 0))

        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#FFFFFF')
        btn_frame.pack(fill='x', pady=20)

        add_btn = tk.Button(
            btn_frame,
            text="➕ Add Student",
            command=self.add_student,
            bg='#27AE60',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=25,
            pady=10,
            cursor='hand2'
        )
        add_btn.pack(side='left', padx=10)

        batch_btn = tk.Button(
            btn_frame,
            text="📋 Add Multiple (CSV)",
            command=self.add_multiple,
            bg='#3498DB',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        batch_btn.pack(side='left', padx=10)

        close_btn = tk.Button(
            btn_frame,
            text="❌ Close",
            command=self.root.destroy,
            bg='#E74C3C',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=25,
            pady=10,
            cursor='hand2'
        )
        close_btn.pack(side='right')

        # Status
        self.status_label = tk.Label(
            form_frame,
            text="Ready to add students",
            bg='#FFFFFF',
            fg='#7F8C8D',
            font=('Segoe UI', 10)
        )
        self.status_label.pack(anchor='w', pady=(10, 0))

        self.generate_id()
        self.bind_keys()

    def generate_id(self):
        """Generate and display new student ID"""
        new_id = self.data_manager.generate_student_id()
        self.id_label.config(text=new_id)
        return new_id

    def bind_keys(self):
        """Keyboard shortcuts"""
        self.root.bind('<Return>', lambda e: self.add_student())
        self.root.bind('<Control-n>', lambda e: self.generate_id())

    def add_student(self):
        """Add single student"""

        name = self.name_entry.get().strip().upper()
        class_name = self.class_entry.get().strip().upper()
        student_id = self.id_label.cget("text")

        if not name or not class_name:
            messagebox.showerror(
                "Error",
                "Name and Class are required!",
                parent=self.root
            )
            return

        if len(name) < 2:
            messagebox.showerror(
                "Error",
                "Name must be at least 2 characters!",
                parent=self.root
            )
            return

        try:
            self.data_manager.add_student(student_id, name, class_name)

            messagebox.showinfo(
                "Success",
                f"Student Added Successfully!\n\nID: {student_id}\nName: {name}\nClass: {class_name}",
                parent=self.root
            )

            self.name_entry.delete(0, tk.END)
            self.class_entry.delete(0, tk.END)

            self.generate_id()
            self.name_entry.focus()

            self.status_label.config(
                text=f"Added: {name} ({student_id})",
                fg='#27AE60'
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to add student:\n{str(e)}",
                parent=self.root
            )

    def add_multiple(self):
        """Add multiple students from CSV"""

        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv *.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            added = 0
            skipped = 0

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                if not line or line.lower().startswith("name"):
                    continue

                parts = [p.strip() for p in line.split(',')]

                if len(parts) < 2:
                    skipped += 1
                    continue

                name = parts[0].upper()
                class_name = parts[1].upper()

                if len(name) < 2:
                    skipped += 1
                    continue

                student_id = self.data_manager.generate_student_id()
                self.data_manager.add_student(student_id, name, class_name)

                added += 1

            messagebox.showinfo(
                "Batch Add Complete",
                f"✅ Added: {added} students\n⚠️ Skipped: {skipped} lines",
                parent=self.root
            )

            self.generate_id()

            self.status_label.config(
                text=f"Batch completed: {added} students added",
                fg='#27AE60'
            )

        except Exception as e:
            messagebox.showerror(
                "Batch Error",
                f"Failed to process file:\n{str(e)}",
                parent=self.root
            )


if __name__ == "__main__":
    app = AddStudentsModule()
    app.root.mainloop()