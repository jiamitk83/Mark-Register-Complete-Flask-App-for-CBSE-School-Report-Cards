
"""
School Mark Register Software
A comprehensive application for managing student marks, subjects, and grades.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from add_students import AddStudentsModule
from data_manager import DataManager

# Professional Color Palette - Light Mode
COLORS = {
    'primary': '#2C3E50',        # Dark blue-gray
    'secondary': '#34495E',      # Medium blue-gray
    'accent': '#3498DB',         # Bright blue
    'success': '#27AE60',        # Green
    'warning': '#F39C12',        # Orange
    'danger': '#E74C3C',         # Red
    'light': '#ECF0F1',          # Light gray
    'dark': '#1A252F',           # Very dark
    'bg_main': '#F5F6FA',        # Main background
    'bg_card': '#FFFFFF',        # Card background
    'text_primary': '#2C3E50',   # Primary text
    'text_secondary': '#7F8C8D', # Secondary text
    'border': '#BDC3C7',         # Border color
}

# Dark Mode Color Palette
DARK_COLORS = {
    'primary': '#1E88E5',        # Bright blue
    'secondary': '#424242',      # Dark gray
    'accent': '#64B5F6',         # Light blue
    'success': '#4CAF50',        # Green
    'warning': '#FFB74D',        # Orange
    'danger': '#EF5350',         # Red
    'light': '#616161',          # Medium gray
    'dark': '#121212',           # Very dark
    'bg_main': '#1E1E1E',        # Main background
    'bg_card': '#2D2D2D',        # Card background
    'text_primary': '#E0E0E0',   # Primary text
    'text_secondary': '#9E9E9E', # Secondary text
    'border': '#424242',         # Border color
}

class MarkRegisterApp:
    """Main Application Class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("School Mark Register")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        self.data_manager = DataManager()
        self.dark_mode = False  # Default to light mode
        self.current_colors = COLORS  # Current color palette
        
        self.setup_styles()
        self.create_header()
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        self.refresh_all()
        
        # Load dark mode preference after UI is created
        self.load_dark_mode_preference()
    
    def setup_styles(self):
        """Configure ttk styles for professional look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Card.TFrame', background=COLORS['bg_card'])
        style.configure('TFrame', background=COLORS['bg_main'])
        
        # Configure Label styles
        style.configure('TLabel', background=COLORS['bg_main'], foreground=COLORS['text_primary'], font=('Segoe UI', 10))
        style.configure('Header.TLabel', background=COLORS['primary'], foreground='white', font=('Segoe UI', 14, 'bold'))
        style.configure('Subheader.TLabel', background=COLORS['bg_main'], foreground=COLORS['text_primary'], font=('Segoe UI', 11, 'bold'))
        style.configure('Status.TLabel', background=COLORS['bg_main'], foreground=COLORS['text_secondary'], font=('Segoe UI', 9))
        
        # Configure Button styles
        style.configure('Primary.TButton', background=COLORS['accent'], foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.configure('Primary.TButton:hover', background='#2980B9')
        style.configure('Success.TButton', background=COLORS['success'], foreground='white', font=('Segoe UI', 10))
        style.configure('Danger.TButton', background=COLORS['danger'], foreground='white', font=('Segoe UI', 10))
        style.configure('TButton', background=COLORS['light'], foreground=COLORS['text_primary'], font=('Segoe UI', 10), borderwidth=1)
        
        # Configure Notebook (Tab) styles
        style.configure('TNotebook', background=COLORS['bg_main'], borderwidth=0)
        style.configure('TNotebook.Tab', background=COLORS['light'], foreground=COLORS['text_primary'], 
                       font=('Segoe UI', 11), padding=[15, 8], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', COLORS['primary'])], 
                 foreground=[('selected', 'white')])
        
        # Configure Treeview styles
        style.configure('Treeview', background='white', foreground=COLORS['text_primary'], 
                       fieldbackground='white', font=('Segoe UI', 10), rowheight=30)
        style.configure('Treeview.Heading', background=COLORS['primary'], foreground='white', 
                       font=('Segoe UI', 10, 'bold'), relief='flat')
        style.map('Treeview', background=[('selected', COLORS['accent'])], 
                 foreground=[('selected', 'white')])
        
        # Configure Labelframe
        style.configure('TLabelframe', background=COLORS['bg_card'], bordercolor=COLORS['border'], font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe.Label', background=COLORS['bg_card'], foreground=COLORS['text_primary'])
        
        # Configure Entry
        style.configure('TEntry', fieldbackground='white', foreground=COLORS['text_primary'], 
                       bordercolor=COLORS['border'], lightcolor=COLORS['accent'], darkcolor=COLORS['border'])
        
        # Configure Combobox
        style.configure('TCombobox', fieldbackground='white', foreground=COLORS['text_primary'], 
                       bordercolor=COLORS['border'], background='white')
        
        # Configure Scrollbar
        style.configure('Vertical.TScrollbar', background=COLORS['light'], troughcolor=COLORS['bg_main'])
        style.configure('Horizontal.TScrollbar', background=COLORS['light'], troughcolor=COLORS['bg_main'])
    
    def create_header(self):
        """Create professional header with branding"""
        header_frame = tk.Frame(self.root, bg=COLORS['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # App icon/logo placeholder
        icon_label = tk.Label(header_frame, text="🎓", bg=COLORS['primary'], fg='white', font=('Segoe UI', 24))
        icon_label.pack(side='left', padx=15, pady=10)
        
        # App title
        title_label = tk.Label(header_frame, text="School Mark Register", 
                              bg=COLORS['primary'], fg='white', 
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(side='left', pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Student Performance Management System", 
                                 bg=COLORS['primary'], fg=COLORS['light'], 
                                 font=('Segoe UI', 9))
        subtitle_label.pack(side='left', padx=10, pady=10)
        
        # Current date/time
        self.date_label = tk.Label(header_frame, text="", bg=COLORS['primary'], fg=COLORS['light'], 
                                  font=('Segoe UI', 9))
        self.date_label.pack(side='right', padx=15, pady=10)
        self.update_date_time()
        
        # Dark mode toggle with switch
        toggle_frame = tk.Frame(header_frame, bg=COLORS['primary'])
        toggle_frame.pack(side='right', padx=15, pady=10)
        
        # Dark mode label
        self.dark_mode_label = tk.Label(toggle_frame, text="Dark Mode", bg=COLORS['primary'], 
                                      fg='white', font=('Segoe UI', 9))
        self.dark_mode_label.pack(side='left', padx=(0, 8))
        
        # Toggle switch canvas
        self.toggle_canvas = tk.Canvas(toggle_frame, width=50, height=24, bg=COLORS['primary'], 
                                       highlightthickness=0, cursor='hand2')
        self.toggle_canvas.pack(side='left')
        
        # Draw the toggle switch
        self.draw_toggle_switch(False)
        
        # Bind click event
        self.toggle_canvas.bind('<Button-1>', lambda e: self.toggle_dark_mode())
    
    def update_date_time(self):
        """Update the date/time display"""
        current_time = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        self.date_label.config(text=current_time)
        self.root.after(1000, self.update_date_time)
    
    def draw_toggle_switch(self, is_dark):
        """Draw the toggle switch visually"""
        self.toggle_canvas.delete('all')
        
        colors = self.current_colors
        
        if is_dark:
            # Dark mode - ON
            # Background track (green when on)
            self.toggle_canvas.create_oval(2, 2, 48, 22, fill='#4CAF50', outline='#388E3C')
            # Knob (circle)
            self.toggle_canvas.create_oval(28, 2, 48, 22, fill='white', outline='#388E3C')
        else:
            # Light mode - OFF
            # Background track (gray when off)
            self.toggle_canvas.create_oval(2, 2, 48, 22, fill='#BDBDBD', outline='#9E9E9E')
            # Knob (circle)
            self.toggle_canvas.create_oval(2, 2, 22, 22, fill='white', outline='#9E9E9E')
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.current_colors = DARK_COLORS
        else:
            self.current_colors = COLORS
        
        # Draw the toggle switch visually
        self.draw_toggle_switch(self.dark_mode)
        
        # Save preference
        self.save_dark_mode_preference()
        
        # Update all UI elements with new colors
        self.apply_theme()
    
    def save_dark_mode_preference(self):
        """Save dark mode preference to data file"""
        self.data_manager.data['settings']['dark_mode'] = self.dark_mode
        self.data_manager.save_data()
    
    def load_dark_mode_preference(self):
        """Load dark mode preference from data file"""
        self.dark_mode = self.data_manager.data.get('settings', {}).get('dark_mode', False)
        if self.dark_mode:
            self.current_colors = DARK_COLORS
            self.draw_toggle_switch(True)
    
    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        colors = self.current_colors
        
        # Update root background
        self.root.configure(bg=colors['bg_main'])
        
        # Update header
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                # Check if it's the header by checking children
                children = widget.winfo_children()
                if children and isinstance(children[0], tk.Label):
                    try:
                        widget.configure(bg=colors['primary'])
                        for child in children:
                            try:
                                if hasattr(child, 'winfo_class'):
                                    if child.winfo_class() == 'Frame':  # toggle frame
                                        child.configure(bg=colors['primary'])
                                    else:
                                        child.configure(bg=colors['primary'], fg='white')
                            except:
                                pass
                    except:
                        pass
        
        # Update notebook/tabs background
        try:
            self.notebook.configure(background=colors['bg_main'])
        except:
            pass
        
        # Update status bar
        try:
            self.status_bar.configure(bg=colors['secondary'])
            self.status_label.configure(bg=colors['secondary'], fg='white')
        except:
            pass
        
        # Update all frames recursively
        self.update_widget_colors(self.root, colors)
        
        # Refresh styles
        self.setup_styles()
    
    def update_widget_colors(self, widget, colors):
        """Recursively update colors of all widgets"""
        # Skip the header frame and toggle canvas
        if hasattr(widget, 'winfo_class'):
            if widget.winfo_class() == 'Canvas':
                return
        
        try:
            # Update frame backgrounds
            if isinstance(widget, tk.Frame):
                # Skip header and toggle frame
                try:
                    bg_color = widget.cget('bg')
                    if bg_color in ['#2C3E50', '#1E88E5', '#34495E', '#424242']:
                        return  # Skip header frames
                except:
                    pass
                widget.configure(bg=colors['bg_card'])
            
            # Update labelframe backgrounds
            if isinstance(widget, tk.LabelFrame):
                widget.configure(bg=colors['bg_card'], fg=colors['text_primary'])
            
            # Update labels
            if isinstance(widget, tk.Label):
                try:
                    bg_color = widget.cget('bg')
                    # Skip header labels
                    if bg_color in ['#2C3E50', '#1E88E5', '#34495E', '#424242', colors['primary'], colors['secondary']]:
                        return
                    # Skip icon labels
                    if widget.cget('text') in ['🎓']:
                        return
                    widget.configure(bg=colors['bg_card'], fg=colors['text_primary'])
                except:
                    pass
            
            # Update listboxes
            if isinstance(widget, tk.Listbox):
                widget.configure(bg=colors['bg_card'], fg=colors['text_primary'], 
                               selectbackground=colors['accent'], selectforeground='white')
            
            # Update entry fields
            if isinstance(widget, tk.Entry):
                widget.configure(bg=colors['bg_card'], fg=colors['text_primary'],
                               insertbackground=colors['text_primary'],
                               fieldbackground=colors['bg_card'])
            
            # Update treeview (results table)
            if widget.winfo_class() == 'Treeview':
                widget.configure(background=colors['bg_card'], 
                               foreground=colors['text_primary'],
                               fieldbackground=colors['bg_card'])
                # Update heading colors
                try:
                    widget.heading('#0', background=colors['primary'], foreground='white')
                    for col in widget['columns']:
                        widget.heading(col, background=colors['primary'], foreground='white')
                except:
                    pass
            
            # Update combobox - through ttk
            if widget.winfo_class() == 'TCombobox':
                widget.configure(fieldbackground=colors['bg_card'],
                               foreground=colors['text_primary'],
                               background=colors['bg_card'])
            
        except:
            pass
        
        # Recursively update children
        try:
            for child in widget.winfo_children():
                self.update_widget_colors(child, colors)
        except:
            pass
    
    def create_menu(self):
        """Create menu bar with professional styling"""
        menubar = tk.Menu(self.root, bg=COLORS['light'], fg=COLORS['text_primary'], 
                         font=('Segoe UI', 10), activebackground=COLORS['accent'], activeforeground='white')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='white', fg=COLORS['text_primary'], 
                           font=('Segoe UI', 10), borderwidth=1)
        menubar.add_cascade(label="📁 File", menu=file_menu, font=('Segoe UI', 10))
        file_menu.add_command(label="📤 Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='white', fg=COLORS['text_primary'], 
                           font=('Segoe UI', 10), borderwidth=1)
        menubar.add_cascade(label="❓ Help", menu=help_menu, font=('Segoe UI', 10))
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.root, bg=COLORS['secondary'], height=25)
        self.status_bar.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                     bg=COLORS['secondary'], fg='white', 
                                     font=('Segoe UI', 9), anchor='w')
        self.status_label.pack(side='left', padx=10, fill='x', expand=True)
        
        # Student count
        self.student_count_label = tk.Label(self.status_bar, text="", 
                                           bg=COLORS['secondary'], fg=COLORS['light'], 
                                           font=('Segoe UI', 9))
        self.student_count_label.pack(side='right', padx=10)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
    
    def create_main_layout(self):
        """Create main application layout with professional styling"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=COLORS['bg_main'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs with padding
        self.tab_students = ttk.Frame(self.notebook, padding=10)
        self.tab_subjects = ttk.Frame(self.notebook, padding=10)
        self.tab_marks = ttk.Frame(self.notebook, padding=10)
        self.tab_results = ttk.Frame(self.notebook, padding=10)
        self.tab_settings = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_students, text="👥 Students")
        self.notebook.add(self.tab_subjects, text="📚 Subjects")
        self.notebook.add(self.tab_marks, text="📝 Marks Entry")
        self.notebook.add(self.tab_results, text="📊 Results")
        self.notebook.add(self.tab_settings, text="⚙️ Settings")
        
        # Setup each tab
        self.setup_students_tab()
        self.setup_subjects_tab()
        self.setup_marks_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
    
    # ==================== STUDENTS TAB ====================
    def setup_students_tab(self):
        """Setup students management tab with professional styling"""
        # Card-like container
        card_frame = tk.Frame(self.tab_students, bg=COLORS['bg_card'], highlightbackground=COLORS['border'], highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Toolbar frame with header
        toolbar = tk.Frame(card_frame, bg=COLORS['bg_card'])
        toolbar.pack(fill='x', padx=15, pady=(15, 10))
        
        # Section title
        title = tk.Label(toolbar, text="Student Management", bg=COLORS['bg_card'], 
                        fg=COLORS['primary'], font=('Segoe UI', 14, 'bold'))
        title.pack(side='left')
        
        # Button frame
        btn_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Styled buttons
        self._create_styled_button(btn_frame, "➕ Add Student", self.open_add_students_window, COLORS['success']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "✏️ Edit Student", self.edit_student, COLORS['accent']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "🗑️ Delete Student", self.delete_student, COLORS['danger']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "🔄 Refresh", self.refresh_students, COLORS['secondary']).pack(side='left', padx=2)
        
        # Treeview frame with border
        tree_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        y_scroll.pack(side='right', fill='y')
        
        # Treeview with styling
        columns = ('ID', 'Name', 'Class')
        self.students_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                          yscrollcommand=y_scroll.set, style='Treeview')
        y_scroll.config(command=self.students_tree.yview)
        
        self.students_tree.heading('ID', text='Student ID')
        self.students_tree.heading('Name', text='Student Name')
        self.students_tree.heading('Class', text='Class')
        
        self.students_tree.column('ID', width=120, anchor='center')
        self.students_tree.column('Name', width=280)
        self.students_tree.column('Class', width=120, anchor='center')
        
        self.students_tree.pack(fill='both', expand=True)
        
        # Add tag for alternating row colors
        self.students_tree.tag_configure('odd', background='#F8F9FA')
        self.students_tree.tag_configure('even', background='white')
    
    def _create_styled_button(self, parent, text, command, bg_color):
        """Create a styled button with hover effect"""
        btn = tk.Button(parent, text=text, command=command, 
                       bg=bg_color, fg='white', font=('Segoe UI', 10),
                       relief='flat', cursor='hand2', padx=12, pady=6,
                       activebackground=self._darken_color(bg_color), activeforeground='white')
        return btn
    
    def _darken_color(self, color):
        """Darken a hex color"""
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, c - 30) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darker)
    
    def refresh_students(self):
        """Refresh students list with styling"""
        self.data_manager.load_data()  # Reload data from file
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = self.data_manager.get_students()
        for idx, (sid, info) in enumerate(sorted(students.items())):
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.students_tree.insert('', 'end', values=(sid, info['name'], info['class']), tags=(tag,))
        
        # Update status
        count = len(students)
        self.student_count_label.config(text=f"Total Students: {count}")
        self.update_status(f"Loaded {count} students")
    
    def open_add_students_window(self):
        """Opens the advanced AddStudentsModule window."""
        add_window = AddStudentsModule(parent_window=self.root)
        self.root.wait_window(add_window.root)  # Wait until the window is closed
        self.refresh_students()  # Refresh the list after adding students
    
    def edit_student(self):
        """Edit selected student with professional dialog"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to edit!")
            return
        
        item = self.students_tree.item(selection[0])
        sid, name, class_name = item['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Student")
        dialog.geometry("500x380")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=COLORS['bg_card'])
        dialog.update_idletasks()
        
        # Header
        header = tk.Frame(dialog, bg=COLORS['accent'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="✏️ Edit Student", bg=COLORS['accent'], fg='white', 
                font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Form
        form_frame = tk.Frame(dialog, bg=COLORS['bg_card'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(form_frame, text="Student ID:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(anchor='w')
        entry_id = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        entry_id.insert(0, sid)
        entry_id.config(state='readonly')
        entry_id.pack(pady=5, fill='x')
        
        tk.Label(form_frame, text="Student Name:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(anchor='w')
        entry_name = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        entry_name.insert(0, name)
        entry_name.pack(pady=5, fill='x')
        
        tk.Label(form_frame, text="Class:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(anchor='w')
        entry_class = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        entry_class.insert(0, class_name)
        entry_class.pack(pady=5, fill='x')
        
        def save():
            new_name = entry_name.get().strip().upper()
            new_class = entry_class.get().strip().upper()
            
            if not new_name or not new_class:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            self.data_manager.update_student(sid, new_name, new_class)
            self.refresh_students()
            dialog.destroy()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.update_status(f"Student {sid} updated")
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg=COLORS['bg_card'])
        btn_frame.pack(side='bottom', pady=10)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg=COLORS['light'], 
                 fg=COLORS['text_primary'], font=('Segoe UI', 10), relief='flat', padx=20, pady=5).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Save", command=save, bg=COLORS['accent'], 
                 fg='white', font=('Segoe UI', 10, 'bold'), relief='flat', padx=20, pady=5).pack(side='left', padx=5)
    
    def delete_student(self):
        """Delete selected student"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to delete!")
            return
        
        item = self.students_tree.item(selection[0])
        sid = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete student {sid}?"):
            self.data_manager.delete_student(sid)
            self.refresh_students()
            messagebox.showinfo("Success", "Student deleted!")
    
    # ==================== SUBJECTS TAB ====================
    def setup_subjects_tab(self):
        """Setup subjects management tab with professional styling"""
        # Card-like container
        card_frame = tk.Frame(self.tab_subjects, bg=COLORS['bg_card'], highlightbackground=COLORS['border'], highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Toolbar frame
        toolbar = tk.Frame(card_frame, bg=COLORS['bg_card'])
        toolbar.pack(fill='x', padx=15, pady=(15, 10))
        
        # Section title
        title = tk.Label(toolbar, text="Subject Management", bg=COLORS['bg_card'], 
                        fg=COLORS['primary'], font=('Segoe UI', 14, 'bold'))
        title.pack(side='left')
        
        # Button frame
        btn_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        self._create_styled_button(btn_frame, "➕ Add Subject", self.add_subject, COLORS['success']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "🗑️ Delete Subject", self.delete_subject, COLORS['danger']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "🔄 Refresh", self.refresh_subjects, COLORS['secondary']).pack(side='left', padx=2)
        
        # Listbox frame
        list_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Styled Listbox
        self.subjects_listbox = tk.Listbox(list_frame, font=('Segoe UI', 11), height=20, 
                                          bg='white', fg=COLORS['text_primary'],
                                          selectbackground=COLORS['accent'],
                                          selectforeground='white',
                                          relief='flat', bd=0,
                                          highlightbackground=COLORS['border'],
                                          highlightthickness=1)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.subjects_listbox.yview)
        self.subjects_listbox.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.subjects_listbox.pack(fill='both', expand=True)
    
    def refresh_subjects(self):
        """Refresh subjects list"""
        self.subjects_listbox.delete(0, 'end')
        subjects = self.data_manager.get_subjects()
        for subject in subjects:
            self.subjects_listbox.insert('end', subject)
    
    def add_subject(self):
        """Add new subject"""
        subject = simpledialog.askstring("Add Subject", "Enter subject name:")
        subject_clean = subject.strip().upper() if subject else ""
        if not subject_clean:
            return
        if not self.data_manager.add_subject(subject_clean):
            messagebox.showerror("Error", "Subject already exists (case-insensitive)!")
            return
        self.refresh_subjects()
        messagebox.showinfo("Success", "Subject added!")
    
    def delete_subject(self):
        """Delete selected subject"""
        selection = self.subjects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a subject!")
            return
        
        subject = self.subjects_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm", f"Delete subject '{subject}'? This will also delete all marks for this subject."):
            self.data_manager.delete_subject(subject)
            self.refresh_subjects()
            messagebox.showinfo("Success", "Subject deleted!")
    
    # ==================== MARKS TAB ====================
    def setup_marks_tab(self):
        """Setup marks entry tab with professional styling"""
        # Card-like container
        card_frame = tk.Frame(self.tab_marks, bg=COLORS['bg_card'], highlightbackground=COLORS['border'], highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Control frame
        control_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        control_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        # Section title
        title = tk.Label(control_frame, text="Marks Entry", bg=COLORS['bg_card'], 
                        fg=COLORS['primary'], font=('Segoe UI', 14, 'bold'))
        title.pack(side='left')
        
        # Cascade selector frame
        cascade_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        cascade_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Exam selector
        exam_frame = tk.Frame(cascade_frame, bg=COLORS['bg_card'])
        exam_frame.pack(side='left', padx=(0,5))
        tk.Label(exam_frame, text="Exam:", bg=COLORS['bg_card'], fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left')
        self.marks_exam_combo = ttk.Combobox(exam_frame, state='readonly', width=12, font=('Segoe UI', 10))
        self.marks_exam_combo.pack(side='left', padx=2)
        self.marks_exam_combo.bind('<<ComboboxSelected>>', self.on_exam_selected)
        
        # Class selector
        class_frame = tk.Frame(cascade_frame, bg=COLORS['bg_card'])
        class_frame.pack(side='left', padx=5)
        tk.Label(class_frame, text="Class:", bg=COLORS['bg_card'], fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left')
        self.marks_class_combo = ttk.Combobox(class_frame, state='readonly', width=12, font=('Segoe UI', 10))
        self.marks_class_combo.pack(side='left', padx=2)
        self.marks_class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        # Subject selector
        subject_frame = tk.Frame(cascade_frame, bg=COLORS['bg_card'])
        subject_frame.pack(side='left', padx=5)
        tk.Label(subject_frame, text="Subject:", bg=COLORS['bg_card'], fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left')
        self.marks_subject_combo = ttk.Combobox(subject_frame, state='readonly', width=12, font=('Segoe UI', 10))
        self.marks_subject_combo.pack(side='left', padx=2)
        self.marks_subject_combo.bind('<<ComboboxSelected>>', self.on_subject_selected)
        
        # Student selector
        student_frame = tk.Frame(cascade_frame, bg=COLORS['bg_card'])
        student_frame.pack(side='left', padx=5)
        tk.Label(student_frame, text="Student:", bg=COLORS['bg_card'], fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left')
        self.marks_student_combo = ttk.Combobox(student_frame, state='readonly', width=20, font=('Segoe UI', 10))
        self.marks_student_combo.pack(side='left', padx=2)
        self.marks_student_combo.bind('<<ComboboxSelected>>', self.on_student_selected)
        
        # Buttons
        btn_frame = tk.Frame(cascade_frame, bg=COLORS['bg_card'])
        btn_frame.pack(side='right', padx=15)
        self._create_styled_button(btn_frame, "🔄 Reset", self.reset_cascade_filters, COLORS['secondary']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "📥 Load Marks", self.load_student_marks, COLORS['accent']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "💾 Save Marks", self.save_marks, COLORS['success']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "📋 Batch Entry", self.batch_marks_entry, COLORS['warning']).pack(side='left', padx=2)
        
        # Marks entry frame
        self.marks_frame = tk.LabelFrame(card_frame, text="Enter Marks", font=('Segoe UI', 10, 'bold'),
                                         bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        self.marks_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.marks_entries = {}
    
    def refresh_cascade_options(self):
        """Refresh cascade dropdown options"""
        # Populate exams (sessions)
        sessions = self.data_manager.get_sessions()
        if not sessions:
            sessions = ["Term 1", "Term 2", "Term 3", "Term 4"]
            for s in sessions:
                self.data_manager.add_session(s)
        self.marks_exam_combo['values'] = sessions
        if sessions:
            self.marks_exam_combo.set(sessions[0])
        
        # Clear downstream combos
        self.marks_class_combo.set('')
        self.marks_subject_combo.set('')
        self.marks_student_combo.set('')
        
        # Clear marks
        for widget in self.marks_frame.winfo_children():
            widget.destroy()
        self.marks_entries.clear()
    
    def refresh_marks_students(self):
        """Refresh student and session dropdowns"""
        self.refresh_cascade_options()
    
    def on_exam_selected(self, event):
        """Handle exam selection - populate classes"""
        self.marks_class_combo['values'] = self.data_manager.get_classes()
        self.marks_class_combo.set('')
        self.marks_subject_combo.set('')
        self.marks_student_combo.set('')
        self.clear_marks_entries()
    
    def on_class_selected(self, event):
        """Handle class selection - populate subjects"""
        self.marks_subject_combo['values'] = self.data_manager.get_subjects()
        self.marks_subject_combo.set('')
        self.marks_student_combo.set('')
        self.clear_marks_entries()
    
    def on_subject_selected(self, event):
        """Handle subject selection - populate students in class"""
        class_selected = self.marks_class_combo.get()
        if class_selected:
            students = self.data_manager.get_students_by_class(class_selected)
            student_list = sorted([f"{sid} - {info['name']}" for sid, info in students.items()], key=lambda x: x.split(' - ')[1])
            self.marks_student_combo['values'] = student_list
            self.marks_student_combo.set('')
        self.clear_marks_entries()
    
    def on_student_selected(self, event):
        """Handle student selection - load marks"""
        exam_selected = self.marks_exam_combo.get()
        if exam_selected:
            self.load_student_marks()
    
    def clear_marks_entries(self):
        """Clear marks entry grid"""
        for widget in self.marks_frame.winfo_children():
            widget.destroy()
        self.marks_entries.clear()
    
    def load_student_marks(self):
        """Load marks for selected student with professional styling"""
        # Clear existing entries
        self.clear_marks_entries()
        
        selection = self.marks_student_combo.get()
        if not selection:
            return
        
        student_id = selection.split(" - ")[0]
        session = self.marks_exam_combo.get()
        subjects = self.data_manager.get_subjects()
        
        if not subjects:
            tk.Label(self.marks_frame, text="No subjects defined. Please add subjects first.", 
                    bg=COLORS['bg_card'], fg=COLORS['warning'], font=('Segoe UI', 11)).pack(pady=20)
            return
        
        # Create entry fields for each subject with styling
        row = 0
        header_frame = tk.Frame(self.marks_frame, bg=COLORS['primary'])
        header_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(header_frame, text="Subject", bg=COLORS['primary'], fg='white', 
                font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=15, pady=8, sticky='w')
        tk.Label(header_frame, text="Marks (0-100)", bg=COLORS['primary'], fg='white', 
                font=('Segoe UI', 10, 'bold')).grid(row=0, column=1, padx=15, pady=8, sticky='w')
        
        student_marks = self.data_manager.get_marks_with_session(student_id, session)
        
        for idx, subject in enumerate(subjects):
            row += 1
            bg_color = COLORS['bg_card'] if idx % 2 == 0 else '#F8F9FA'
            
            row_frame = tk.Frame(self.marks_frame, bg=bg_color)
            row_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=2)
            
            tk.Label(row_frame, text=subject, bg=bg_color, fg=COLORS['text_primary'], 
                    font=('Segoe UI', 10), width=25, anchor='w').grid(row=0, column=0, padx=10, pady=5)
            
            entry = ttk.Entry(row_frame, width=15, font=('Segoe UI', 10))
            entry.grid(row=0, column=1, padx=10, pady=5)
            
            # Pre-fill existing marks
            if subject in student_marks:
                entry.insert(0, str(student_marks[subject]))
            
            self.marks_entries[subject] = entry
        
        self.update_status(f"Loaded marks for {selection}")
    
    def save_marks(self):
        """Save marks for current student"""
        selection = self.marks_student_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student!")
            return
        
        student_id = selection.split(" - ")[0]
        session = self.marks_exam_combo.get()
        
        if not session:
            messagebox.showwarning("Warning", "Please select an exam!")
            return
        
        for subject, entry in self.marks_entries.items():
            try:
                marks = float(entry.get()) if entry.get().strip() else 0
                if marks < 0 or marks > 100:
                    messagebox.showerror("Error", f"Marks for {subject} must be between 0 and 100!")
                    return
                self.data_manager.set_marks_with_session(student_id, session, subject, marks)
            except ValueError:
                messagebox.showerror("Error", f"Invalid marks value for {subject}!")
                return
        
        messagebox.showinfo("Success", f"Marks saved successfully for {session}!")
        self.update_status(f"Marks saved for {selection} - {session}")
    
    def batch_marks_entry(self):
        """Open batch marks entry for all students in a class for a subject"""
        session = self.marks_exam_combo.get()
        class_selected = self.marks_class_combo.get()
        subject = self.marks_subject_combo.get()
        
        if not session:
            messagebox.showwarning("Warning", "Please select an Exam (Term)!")
            return
        
        if not class_selected:
            messagebox.showwarning("Warning", "Please select a Class!")
            return
        
        if not subject:
            messagebox.showwarning("Warning", "Please select a Subject!")
            return
        
        # Get all students in the selected class
        students = self.data_manager.get_students_by_class(class_selected)
        if not students:
            messagebox.showwarning("Warning", "No students found in this class!")
            return
        
        # Create batch entry window
        batch_window = tk.Toplevel(self.root)
        batch_window.title(f"Batch Marks Entry - {session} - {subject}")
        batch_window.geometry("600x500")
        batch_window.transient(self.root)
        
        # Header
        header_frame = tk.Frame(batch_window, bg=COLORS['primary'])
        header_frame.pack(fill='x')
        tk.Label(header_frame, text=f"Batch Marks Entry: {session} - {subject} - Class {class_selected}", 
                bg=COLORS['primary'], fg='white', font=('Segoe UI', 12, 'bold'), padx=10, pady=10).pack()
        
        # Table frame
        table_frame = tk.Frame(batch_window)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('student_id', 'name', 'marks')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        tree.heading('student_id', text='ID')
        tree.heading('name', text='Student Name')
        tree.heading('marks', text='Marks')
        tree.column('student_id', width=80)
        tree.column('name', width=250)
        tree.column('marks', width=100)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        # Get existing marks
        existing_marks = {}
        for student_id in students.keys():
            student_marks = self.data_manager.get_marks_with_session(student_id, session)
            if subject in student_marks:
                existing_marks[student_id] = student_marks[subject]
        
        # Populate tree
        student_entries = {}
        for sid in sorted(students.keys()):
            name = students[sid]['name']
            tree.insert('', 'end', values=(sid, name, ''))
        
        # Add entry widgets in the marks column
        def on_tree_select(event):
            """Handle tree selection"""
            pass
        
        tree.bind('<Button-1>', lambda e: tree.selection())  # Just bind for selection
        
        # Buttons frame
        btn_frame = tk.Frame(batch_window, bg=COLORS['bg_main'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        # Get max marks for validation
        max_marks = self.data_manager.get_exam_max_marks(subject, session)
        
        tk.Label(btn_frame, text=f"Max Marks: {max_marks}", bg=COLORS['bg_main'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left', padx=10)
        
        def save_batch_marks():
            """Save marks for all students"""
            # Get all item values from tree
            saved_count = 0
            for item in tree.get_children():
                values = tree.item(item, 'values')
                student_id = values[0]
                marks_value = values[2] if len(values) > 2 else ''
                
                if marks_value and marks_value.strip():
                    try:
                        marks = float(marks_value)
                        if marks < 0 or marks > max_marks:
                            messagebox.showerror("Error", f"Marks for {values[1]} must be between 0 and {max_marks}!")
                            return
                        self.data_manager.set_marks_with_session(student_id, session, subject, marks)
                        saved_count += 1
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid marks for {values[1]}!")
                        return
            
            messagebox.showinfo("Success", f"Marks saved for {saved_count} students!")
            self.refresh_results()
            batch_window.destroy()
        
        def update_marks_in_tree(event):
            """Update marks in tree when edited"""
            # Get the clicked column and item
            region = tree.identify_region(event.x, event.y)
            if region == 'cell':
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                if column == '#3':  # Marks column
                    # Open editor
                    x, y, width, height = tree.bbox(item, column)
                    current_value = tree.set(item, 'marks')
                    
                    entry_editor = tk.Entry(tree, width=width//8, fg='black', bg='white')
                    entry_editor.insert(0, current_value)
                    entry_editor.select_range(0, tk.END)
                    
                    entry_editor.place(x=x, y=y, width=width, height=height)
                    entry_editor.focus_set()
                    
                    def save_edit(event):
                        new_value = entry_editor.get()
                        tree.set(item, 'marks', new_value)
                        entry_editor.destroy()
                    
                    entry_editor.bind('<Return>', save_edit)
                    entry_editor.bind('<FocusOut>', save_edit)
        
        tree.bind('<Button-1>', update_marks_in_tree)
        
        self._create_styled_button(btn_frame, "💾 Save All Marks", save_batch_marks, COLORS['success']).pack(side='right', padx=5)
        self._create_styled_button(btn_frame, "❌ Cancel", batch_window.destroy, COLORS['danger']).pack(side='right', padx=5)
        
        # Load existing marks into tree
        for item in tree.get_children():
            sid = tree.item(item, 'values')[0]
            if sid in existing_marks:
                tree.set(item, 'marks', str(existing_marks[sid]))
    
    # ==================== RESULTS TAB ====================
    def setup_results_tab(self):
        """Setup results/reports tab with professional styling"""
        # Card-like container
        card_frame = tk.Frame(self.tab_results, bg=COLORS['bg_card'], highlightbackground=COLORS['border'], highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Toolbar
        toolbar = tk.Frame(card_frame, bg=COLORS['bg_card'])
        toolbar.pack(fill='x', padx=15, pady=(15, 10))
        
        # Section title
        title = tk.Label(toolbar, text="Student Results & Reports", bg=COLORS['bg_card'], 
                        fg=COLORS['primary'], font=('Segoe UI', 14, 'bold'))
        title.pack(side='left')
        
        # Button frame
        btn_frame = tk.Frame(card_frame, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Session selector for results
        session_label = tk.Label(btn_frame, text="Select Exam:", bg=COLORS['bg_card'], 
                                fg=COLORS['text_primary'], font=('Segoe UI', 10))
        session_label.pack(side='left', padx=(0, 5))
        
        self.results_session_combo = ttk.Combobox(btn_frame, state='readonly', width=15, font=('Segoe UI', 10))
        self.results_session_combo.pack(side='left', padx=5)
        
        self._create_styled_button(btn_frame, "📊 Generate Results", self.generate_all_results, COLORS['accent']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "📤 Export to Text", self.export_results, COLORS['success']).pack(side='left', padx=2)
        self._create_styled_button(btn_frame, "🔄 Refresh", self.refresh_results, COLORS['secondary']).pack(side='left', padx=2)
        
        # Results display
        results_container = tk.Frame(card_frame, bg=COLORS['bg_card'])
        results_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.results_text = tk.Text(results_container, wrap='none', font=('Consolas', 10), 
                                    bg='#2C3E50', fg='#ECF0F1', relief='flat',
                                    insertbackground='white')
        scrollbar_y = ttk.Scrollbar(results_container, orient='vertical', command=self.results_text.yview)
        scrollbar_x = ttk.Scrollbar(results_container, orient='horizontal', command=self.results_text.xview)
        
        self.results_text.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        self.results_text.pack(fill='both', expand=True)
    
    def generate_all_results(self):
        """Generate results for all students with professional formatting"""
        self.results_text.delete('1.0', 'end')
        
        students = self.data_manager.get_students()
        subjects = self.data_manager.get_subjects()
        session = self.results_session_combo.get()
        
        if not students:
            self.results_text.insert('end', "⚠️  No students found!\n")
            return
        
        if not subjects:
            self.results_text.insert('end', "⚠️  No subjects defined!\n")
            return
        
        passing_marks = self.data_manager.get_passing_marks()
        
        # Header with styling
        header = "=" * 90
        self.results_text.insert('end', header + "\n")
        self.results_text.insert('end', "                    📊 SCHOOL MARK REGISTER - STUDENT RESULTS\n")
        self.results_text.insert('end', f"                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if session:
            self.results_text.insert('end', f"                    Exam Session: {session}\n")
        self.results_text.insert('end', f"                    Passing Marks: {passing_marks}%\n")
        self.results_text.insert('end', header + "\n\n")
        
        for sid, info in sorted(students.items()):
            result = self.data_manager.calculate_student_result(sid, session)
            
            # Student info with emoji
            self.results_text.insert('end', f"👤 Student ID: {sid}\n")
            self.results_text.insert('end', f"📛 Name: {info['name']}\n")
            self.results_text.insert('end', f"🏫 Class: {info['class']}\n")
            self.results_text.insert('end', "-" * 50 + "\n")
            
            if result:
                self.results_text.insert('end', "📚 MARKS:\n")
                for subject in subjects:
                    marks = result['marks'].get(subject, 'N/A')
                    self.results_text.insert('end', f"   ▸ {subject}: {marks}\n")
                
                self.results_text.insert('end', "-" * 50 + "\n")
                self.results_text.insert('end', f"📈 Total Marks: {result['total']} / {result['max_total']}\n")
                self.results_text.insert('end', f"📉 Average: {result['average']}\n")
                self.results_text.insert('end', f"📊 Percentage: {result['percentage']}%\n")
                self.results_text.insert('end', f"🏅 Grade: {result['grade']}\n")
                
                # Pass/Fail status
                status = "✅ PASS" if result['is_pass'] else "❌ FAIL"
                status_color = "#27AE60" if result['is_pass'] else "#E74C3C"
                self.results_text.insert('end', f"📋 Status: {status}\n")
            else:
                self.results_text.insert('end', "   No marks recorded.\n")
            
            self.results_text.insert('end', "\n" + "=" * 90 + "\n\n")
        
        self.update_status("Results generated successfully")
    
    def export_results(self):
        """Export results to text file"""
        content = self.results_text.get('1.0', 'end')
        if not content.strip():
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def refresh_results(self):
        """Refresh results display"""
        # Populate session dropdown
        sessions = self.data_manager.get_sessions()
        if sessions:
            self.results_session_combo['values'] = sessions
            self.results_session_combo.set(sessions[0])
        self.generate_all_results()
    
    # ==================== SETTINGS TAB ====================
    def setup_settings_tab(self):
        """Setup settings tab for configuring exams, passing marks and grades"""
        # Card-like container
        card_frame = tk.Frame(self.tab_settings, bg=COLORS['bg_card'], highlightbackground=COLORS['border'], highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Title
        title = tk.Label(card_frame, text="⚙️ Exam & Grade Settings", bg=COLORS['bg_card'], 
                        fg=COLORS['primary'], font=('Segoe UI', 14, 'bold'))
        title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Settings container with two columns
        settings_container = tk.Frame(card_frame, bg=COLORS['bg_card'])
        settings_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Left column - Exam Sessions
        left_frame = tk.LabelFrame(settings_container, text="📅 Exam Sessions", font=('Segoe UI', 11, 'bold'),
                                   bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Add or remove exam sessions (e.g., Term 1, Term 2, etc.)", 
                bg=COLORS['bg_card'], fg=COLORS['text_secondary'], font=('Segoe UI', 9)).pack(anchor='w', padx=10, pady=(5, 10))
        
        self.session_listbox = tk.Listbox(left_frame, height=8, font=('Segoe UI', 10))
        self.session_listbox.pack(fill='x', padx=10, pady=5)
        
        session_btn_frame = tk.Frame(left_frame, bg=COLORS['bg_card'])
        session_btn_frame.pack(fill='x', padx=10, pady=5)
        
        self._create_styled_button(session_btn_frame, "➕ Add Session", self.add_session, COLORS['success']).pack(side='left', padx=2)
        self._create_styled_button(session_btn_frame, "➖ Remove", self.remove_session, COLORS['danger']).pack(side='left', padx=2)
        
        # Middle column - Passing Marks
        middle_frame = tk.LabelFrame(settings_container, text="✅ Passing Criteria", font=('Segoe UI', 11, 'bold'),
                                     bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        middle_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(middle_frame, text="Set minimum passing percentage", 
                bg=COLORS['bg_card'], fg=COLORS['text_secondary'], font=('Segoe UI', 9)).pack(anchor='w', padx=10, pady=(5, 10))
        
        passing_frame = tk.Frame(middle_frame, bg=COLORS['bg_card'])
        passing_frame.pack(anchor='w', padx=10, pady=5)
        
        tk.Label(passing_frame, text="Passing Marks (%):", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        
        self.passing_marks_var = tk.StringVar(value="35")
        passing_entry = tk.Entry(passing_frame, textvariable=self.passing_marks_var, width=10, font=('Segoe UI', 10))
        passing_entry.pack(side='left', padx=5)
        
        self._create_styled_button(passing_frame, "💾 Save", self.save_passing_marks, COLORS['accent']).pack(side='left', padx=5)
        
        # Current passing status
        self.passing_status_label = tk.Label(middle_frame, text="", bg=COLORS['bg_card'], 
                                            fg=COLORS['success'], font=('Segoe UI', 9))
        self.passing_status_label.pack(anchor='w', padx=10, pady=5)
        
        # Right column - Grade Boundaries
        right_frame = tk.LabelFrame(settings_container, text="🏅 Grade Boundaries", font=('Segoe UI', 11, 'bold'),
                                    bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        right_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(right_frame, text="Set minimum percentage for each grade", 
                bg=COLORS['bg_card'], fg=COLORS['text_secondary'], font=('Segoe UI', 9)).pack(anchor='w', padx=10, pady=(5, 10))
        
        # Grade entries
        grades = [('A+', 90), ('A', 80), ('B+', 70), ('B', 60), ('C', 50), ('D', 40)]
        self.grade_entries = {}
        
        for grade, default in grades:
            row_frame = tk.Frame(right_frame, bg=COLORS['bg_card'])
            row_frame.pack(fill='x', padx=10, pady=2)
            
            tk.Label(row_frame, text=f"{grade} (min %):", bg=COLORS['bg_card'], 
                    fg=COLORS['text_primary'], font=('Segoe UI', 10), width=12, anchor='w').pack(side='left')
            
            entry = tk.Entry(row_frame, width=10, font=('Segoe UI', 10))
            entry.insert(0, str(default))
            entry.pack(side='left', padx=5)
            self.grade_entries[grade] = entry
        
        self._create_styled_button(right_frame, "💾 Save Grades", self.save_grade_boundaries, COLORS['accent']).pack(pady=10)
        
        # Grade status
        self.grade_status_label = tk.Label(right_frame, text="", bg=COLORS['bg_card'], 
                                          fg=COLORS['success'], font=('Segoe UI', 9))
        self.grade_status_label.pack()
        
        # ==================== MAX MARKS SECTION ====================
        # New row for Max Marks configuration
        max_marks_frame = tk.LabelFrame(card_frame, text="📝 Max Marks per Subject", font=('Segoe UI', 11, 'bold'),
                                       bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        max_marks_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(max_marks_frame, text="Set maximum marks for each subject in each term", 
                bg=COLORS['bg_card'], fg=COLORS['text_secondary'], font=('Segoe UI', 9)).pack(anchor='w', padx=10, pady=(5, 10))
        
        # Selection row
        selection_row = tk.Frame(max_marks_frame, bg=COLORS['bg_card'])
        selection_row.pack(fill='x', padx=10, pady=5)
        
        tk.Label(selection_row, text="Term:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        
        self.max_marks_session_var = tk.StringVar()
        self.max_marks_session_combo = ttk.Combobox(selection_row, textvariable=self.max_marks_session_var, 
                                                     width=15, state='readonly', font=('Segoe UI', 10))
        self.max_marks_session_combo.pack(side='left', padx=5)
        self.max_marks_session_combo.bind('<<ComboboxSelected>>', self.on_max_marks_session_changed)
        
        tk.Label(selection_row, text="Subject:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left', padx=(15, 5))
        
        self.max_marks_subject_var = tk.StringVar()
        self.max_marks_subject_combo = ttk.Combobox(selection_row, textvariable=self.max_marks_subject_var, 
                                                     width=20, state='readonly', font=('Segoe UI', 10))
        self.max_marks_subject_combo.pack(side='left', padx=5)
        self.max_marks_subject_combo.bind('<<ComboboxSelected>>', self.on_max_marks_subject_changed)
        
        tk.Label(selection_row, text="Max Marks:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 10)).pack(side='left', padx=(15, 5))
        
        self.max_marks_value_var = tk.StringVar(value="100")
        self.max_marks_entry = tk.Entry(selection_row, textvariable=self.max_marks_value_var, width=10, font=('Segoe UI', 10))
        self.max_marks_entry.pack(side='left', padx=5)
        
        self._create_styled_button(selection_row, "💾 Save", self.save_max_marks, COLORS['accent']).pack(side='left', padx=10)
        
        # Status label
        self.max_marks_status_label = tk.Label(max_marks_frame, text="", bg=COLORS['bg_card'], 
                                              fg=COLORS['success'], font=('Segoe UI', 9))
        self.max_marks_status_label.pack(anchor='w', padx=10, pady=(0, 10))
        
        # Current max marks display
        self.max_marks_tree_frame = tk.Frame(max_marks_frame, bg=COLORS['bg_card'])
        self.max_marks_tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        max_marks_scroll = ttk.Scrollbar(self.max_marks_tree_frame)
        max_marks_scroll.pack(side='right', fill='y')
        
        self.max_marks_tree = ttk.Treeview(self.max_marks_tree_frame, columns=('term', 'subject', 'max_marks'), 
                                           show='headings', height=6, yscrollcommand=max_marks_scroll.set)
        self.max_marks_tree.heading('term', text='Term')
        self.max_marks_tree.heading('subject', text='Subject')
        self.max_marks_tree.heading('max_marks', text='Max Marks')
        self.max_marks_tree.column('term', width=120)
        self.max_marks_tree.column('subject', width=150)
        self.max_marks_tree.column('max_marks', width=100)
        self.max_marks_tree.pack(side='left', fill='both', expand=True)
        max_marks_scroll.config(command=self.max_marks_tree.yview)
        
        # Load current settings
        self.refresh_settings()
    
    def refresh_settings(self):
        """Refresh settings display"""
        # Load sessions
        sessions = self.data_manager.get_sessions()
        self.session_listbox.delete(0, 'end')
        for s in sessions:
            self.session_listbox.insert('end', s)
        
        # Load passing marks
        passing = self.data_manager.get_passing_marks()
        self.passing_marks_var.set(str(passing))
        self.passing_status_label.config(text=f"Current passing marks: {passing}%")
        
        # Load grade boundaries
        boundaries = self.data_manager.get_grade_boundaries()
        for grade, entry in self.grade_entries.items():
            if grade in boundaries:
                entry.delete(0, 'end')
                entry.insert(0, str(boundaries[grade]))
        self.grade_status_label.config(text="Grade boundaries loaded")
        
        # Load max marks comboboxes
        self.populate_max_marks_comboboxes()
        self.populate_max_marks_tree()
    
    def add_session(self):
        """Add a new exam session"""
        from tkinter import simpledialog
        session = simpledialog.askstring("Add Session", "Enter exam session name (e.g., Term 1, Mid-term, Final):")
        if session and session.strip():
            self.data_manager.add_session(session.strip().upper())
            self.session_listbox.insert('end', session.strip().upper())
            self.refresh_marks_students()
            self.refresh_results()
            messagebox.showinfo("Success", f"Session '{session.strip().upper()}' added!")
    
    def remove_session(self):
        """Remove selected session"""
        selection = self.session_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session to remove!")
            return
        
        session = self.session_listbox.get(selection[0])
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete session '{session}'? All marks for this session will be deleted.")
        if confirm:
            self.data_manager.delete_session(session)
            self.session_listbox.delete(selection[0])
            self.refresh_marks_students()
            self.refresh_results()
            messagebox.showinfo("Success", f"Session '{session}' removed!")
    
    def save_passing_marks(self):
        """Save passing marks setting"""
        try:
            passing = int(self.passing_marks_var.get())
            if passing < 0 or passing > 100:
                messagebox.showerror("Error", "Passing marks must be between 0 and 100!")
                return
            self.data_manager.set_passing_marks(passing)
            self.passing_status_label.config(text=f"✓ Saved! Passing marks: {passing}%")
            self.refresh_results()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def save_grade_boundaries(self):
        """Save grade boundaries"""
        boundaries = {}
        try:
            for grade, entry in self.grade_entries.items():
                value = int(entry.get())
                if value < 0 or value > 100:
                    messagebox.showerror("Error", f"Grade {grade} must be between 0 and 100!")
                    return
                boundaries[grade] = value
            
            # Sort by value descending and add F grade
            sorted_grades = sorted(boundaries.items(), key=lambda x: x[1], reverse=True)
            final_boundaries = {}
            prev_value = 100
            for grade, value in sorted_grades:
                final_boundaries[grade] = value
                prev_value = value
            final_boundaries['F'] = 0
            
            self.data_manager.set_grade_boundaries(final_boundaries)
            self.grade_status_label.config(text="✓ Grade boundaries saved!")
            self.refresh_results()
            messagebox.showinfo("Success", "Grade boundaries saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def on_max_marks_session_changed(self, event=None):
        """Handle session selection change for max marks"""
        self.populate_max_marks_tree()
    
    def on_max_marks_subject_changed(self, event=None):
        """Handle subject selection change for max marks"""
        session = self.max_marks_session_var.get()
        subject = self.max_marks_subject_var.get()
        if session and subject:
            # Load existing max marks for this combination
            max_marks = self.data_manager.get_exam_max_marks(subject, session)
            self.max_marks_value_var.set(str(max_marks))
    
    def populate_max_marks_comboboxes(self):
        """Populate session and subject comboboxes for max marks"""
        sessions = self.data_manager.get_sessions()
        subjects = self.data_manager.get_subjects()
        
        self.max_marks_session_combo['values'] = sessions
        self.max_marks_subject_combo['values'] = subjects
        
        if sessions:
            self.max_marks_session_var.set(sessions[0])
        if subjects:
            self.max_marks_subject_var.set(subjects[0])
    
    def populate_max_marks_tree(self):
        """Populate the max marks tree view with current settings"""
        # Clear existing items
        for item in self.max_marks_tree.get_children():
            self.max_marks_tree.delete(item)
        
        # Get all configured max marks
        exam_max_marks = self.data_manager.data.get('settings', {}).get('exam_max_marks', {})
        
        sessions = self.data_manager.get_sessions()
        subjects = self.data_manager.get_subjects()
        
        for session in sessions:
            for subject in subjects:
                key = f"{subject}_{session}"
                max_marks = exam_max_marks.get(key)
                if max_marks is not None:
                    self.max_marks_tree.insert('', 'end', values=(session, subject, max_marks))
    
    def save_max_marks(self):
        """Save max marks for selected subject and session"""
        session = self.max_marks_session_var.get()
        subject = self.max_marks_subject_var.get()
        
        if not session or not subject:
            messagebox.showwarning("Warning", "Please select both Term and Subject!")
            return
        
        try:
            max_marks = int(self.max_marks_value_var.get())
            if max_marks < 1 or max_marks > 1000:
                messagebox.showerror("Error", "Max marks must be between 1 and 1000!")
                return
            
            self.data_manager.set_exam_max_marks(subject, session, max_marks)
            self.max_marks_status_label.config(text=f"✓ Saved! {subject} - {session}: {max_marks} marks")
            self.populate_max_marks_tree()
            self.refresh_results()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    # ==================== GENERAL METHODS ====================
    def reset_cascade_filters(self):
        """Reset all cascade filters"""
        self.marks_exam_combo.set('')
        self.marks_class_combo.set('')
        self.marks_subject_combo.set('')
        self.marks_student_combo.set('')
        self.clear_marks_entries()
        self.update_status("Filters reset")
    
    def refresh_all(self):
        """Refresh all tabs"""
        self.refresh_students()
        self.refresh_subjects()
        self.refresh_cascade_options()
        self.refresh_results()
        self.refresh_settings()
        self.update_status("Application loaded successfully")
    
    def export_data(self):
        """Export all data to JSON"""
        try:
            export_file = f"mark_register_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w') as f:
                json.dump(self.data_manager.data, f, indent=4)
            messagebox.showinfo("Success", f"Data exported to {export_file}")
            self.update_status(f"Data exported to {export_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def show_about(self):
        """Show about dialog with professional styling"""
        about_win = tk.Toplevel(self.root)
        about_win.title("About")
        about_win.geometry("400x250")
        about_win.resizable(False, False)
        about_win.transient(self.root)
        about_win.grab_set()
        
        # Background
        about_win.configure(bg=COLORS['bg_card'])
        
        # Header
        header = tk.Frame(about_win, bg=COLORS['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🎓", bg=COLORS['primary'], fg='white', font=('Segoe UI', 32)).pack(pady=5)
        tk.Label(header, text="School Mark Register", bg=COLORS['primary'], fg='white', 
                font=('Segoe UI', 16, 'bold')).pack()
        
        # Content
        content = tk.Frame(about_win, bg=COLORS['bg_card'])
        content.pack(fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(content, text="Version 1.0", bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
                font=('Segoe UI', 10)).pack()
        
        tk.Label(content, text="Student Performance Management System", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Segoe UI', 11)).pack(pady=10)
        
        tk.Label(content, text="A comprehensive solution for managing student marks, subjects, and grades.", 
                bg=COLORS['bg_card'], fg=COLORS['text_secondary'], font=('Segoe UI', 9), 
                wraplength=300, justify='center').pack(pady=5)
        
        tk.Label(content, text="© 2024 School Mark Register", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Segoe UI', 8)).pack(side='bottom', pady=10)


def main():
    """Main entry point with professional window settings"""
    root = tk.Tk()
    
    # Set window background
    root.configure(bg=COLORS['bg_main'])
    
    app = MarkRegisterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
