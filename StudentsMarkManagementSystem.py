#updated executable code 
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Connect to SQLite database
conn = sqlite3.connect('student_data.db')
cursor = conn.cursor()

# Function to create student table if not exists
def create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students59 (
            roll_number INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            DAA REAL,
            IWT REAL,
            Python REAL,
            SEPD REAL,
            total_marks REAL,
            grade TEXT
        )
    ''')
    conn.commit()

# Function to add marks securely
def add_marks():
    pin = pin_entry.get()
    if pin != '1234':  # Replace '1234' with your actual secure PIN
        messagebox.showerror('Error', 'Enter correct 4 digit pin!')
        return
    
    name = name_entry.get()
    roll_number = int(roll_entry.get())
    daa_marks = float(daa_entry.get())
    iwt_marks = float(iwt_entry.get())
    python_marks = float(python_entry.get())
    sepd_marks = float(sepd_entry.get())
    
    total_marks = daa_marks + iwt_marks + python_marks + sepd_marks
    grade = calculate_grade(total_marks)
    
    # Insert or replace student data in SQLite table
    cursor.execute('''
        INSERT OR REPLACE INTO students59 (roll_number, name, DAA, IWT, Python, SEPD, total_marks, grade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (roll_number, name, daa_marks, iwt_marks, python_marks, sepd_marks, total_marks, grade))
    
    conn.commit()
    messagebox.showinfo('Success', 'Marks added successfully!')
    fetch_student_data()

# Function to fetch all student data from SQLite
def fetch_student_data():
    try:
        cursor.execute('SELECT * FROM students59')
        data = cursor.fetchall()
        show_data_dialog(data)
    except sqlite3.Error as e:
        messagebox.showwarning('Warning', f'Error fetching data: {e}')

# Function to fetch and display individual student data based on roll number
def fetch_individual_data():
    roll_number = int(roll_view_entry.get())
    try:
        cursor.execute('SELECT * FROM students59 WHERE roll_number = ?', (roll_number,))
        data = cursor.fetchone()
        
        if data:
            calculate_marks(data)
            show_individual_data_dialog(data)
        else:
            messagebox.showerror('Error', 'Student not found!')
    
    except sqlite3.Error as e:
        messagebox.showerror('Error', f'Error fetching data: {e}')

# Function to calculate total marks and grade
def calculate_marks(data):
    daa_marks = data[2]
    iwt_marks = data[3]
    python_marks = data[4]
    sepd_marks = data[5]
    
    total_marks = daa_marks + iwt_marks + python_marks + sepd_marks
    grade = calculate_grade(total_marks)
    
    cursor.execute('''
        UPDATE students59
        SET total_marks = ?, grade = ?
        WHERE roll_number = ?
    ''', (total_marks, grade, data[0]))
    
    conn.commit()

# Function to calculate grade based on total marks
def calculate_grade(total_marks):
    if total_marks >= 360:
        return 'A'
    elif total_marks >= 300:
        return 'B'
    elif total_marks >= 240:
        return 'C'
    elif total_marks >= 180:
        return 'D'
    else:
        return 'F'

# Function to generate PDF with formatted table and headings
def generate_pdf():
    roll_number = int(roll_pdf_entry.get())
    
    try:
        cursor.execute('SELECT * FROM students59 WHERE roll_number = ?', (roll_number,))
        data = cursor.fetchone()
        
        if data:
            pdf_filename = f'student_marksheet_{data[0]}.pdf'
            
            # Define styles for headings
            styles = getSampleStyleSheet()
            TitleStyle = ParagraphStyle(
                name='TitleStyle',
                parent=styles['Title'],
                fontSize=18,
                alignment=1,  # Center align
                spaceAfter=12
            )
            SubTitleStyle = ParagraphStyle(
                name='SubTitleStyle',
                parent=styles['Heading2'],
                fontSize=14,
                alignment=1,  # Center align
                spaceAfter=12
            )
            
            # Create a PDF document
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            
            # Data for the table
            table_data = [
                ['Name', data[1]],
                ['Roll Number', data[0]],
                ['DAA Marks', data[2]],
                ['IWT Marks', data[3]],
                ['Python Marks', data[4]],
                ['SEPD Marks', data[5]],
                ['Total Marks', data[6]],
                ['Grade', data[7]]
            ]
            
            # Create a Table with the data
            table = Table(table_data)
            
            # Add TableStyle to the Table for formatting
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12)
            ]))
            
            # Build the PDF with the heading, subheading, and table
            content = []
            content.append(Paragraph('GANDHI INSTITUTE FOR TECHNOLOGY, GANGAPADA, KHORDHA', TitleStyle))
            content.append(Paragraph('Academic Marks', SubTitleStyle))
            content.append(table)
            
            doc.build(content)
            
            messagebox.showinfo('Success', f'PDF generated: {pdf_filename}')
        else:
            messagebox.showerror('Error', 'Student not found!')
    
    except sqlite3.Error as e:
        messagebox.showerror('Error', f'Error fetching data: {e}')

# Function to show data in a dialog
def show_data_dialog(data):
    data_window = tk.Toplevel(root)
    data_window.title('All Students Data')
    
    text_area = scrolledtext.ScrolledText(data_window, width=80, height=20)
    text_area.pack(padx=10, pady=10)
    
    for row in data:
        text_area.insert(tk.END, f'Roll Number: {row[0]}, Name: {row[1]}, DAA: {row[2]}, IWT: {row[3]}, Python: {row[4]}, SEPD: {row[5]}, Total Marks: {row[6]}, Grade: {row[7]}\n')
    
    text_area.config(state=tk.DISABLED)

# Function to show individual student data in a dialog
def show_individual_data_dialog(data):
    individual_data_window = tk.Toplevel(root)
    individual_data_window.title('Individual Student Data')
    
    text_area = scrolledtext.ScrolledText(individual_data_window, width=80, height=10)
    text_area.pack(padx=10, pady=10)
    
    text_area.insert(tk.END, f'Roll Number: {data[0]}\n')
    text_area.insert(tk.END, f'Name: {data[1]}\n')
    text_area.insert(tk.END, f'DAA Marks: {data[2]}\n')
    text_area.insert(tk.END, f'IWT Marks: {data[3]}\n')
    text_area.insert(tk.END, f'Python Marks: {data[4]}\n')
    text_area.insert(tk.END, f'SEPD Marks: {data[5]}\n')
    text_area.insert(tk.END, f'Total Marks: {data[6]}\n')
    text_area.insert(tk.END, f'Grade: {data[7]}\n')
    
    text_area.config(state=tk.DISABLED)

# Tkinter GUI setup
root = tk.Tk()
root.title('Student Marks Management')

# Ensure the table is created
create_table()

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill='both', expand=True)

# Existing tab for adding/viewing marks
add_view_tab = tk.Frame(notebook)
notebook.add(add_view_tab, text='Add/View Marks')

# Add Marks Frame
add_marks_frame = tk.LabelFrame(add_view_tab, text='Add Marks')
add_marks_frame.pack(padx=10, pady=10, fill='both', expand=True, anchor='center')

tk.Label(add_marks_frame, text='Security PIN:').grid(row=0, column=0, padx=5, pady=5)
pin_entry = tk.Entry(add_marks_frame, show='•')
pin_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='Name:').grid(row=1, column=0, padx=5, pady=5)
name_entry = tk.Entry(add_marks_frame)
name_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='Roll Number:').grid(row=2, column=0, padx=5, pady=5)
roll_entry = tk.Entry(add_marks_frame)
roll_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='DAA Marks:').grid(row=3, column=0, padx=5, pady=5)
daa_entry = tk.Entry(add_marks_frame)
daa_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='IWT Marks:').grid(row=4, column=0, padx=5, pady=5)
iwt_entry = tk.Entry(add_marks_frame)
iwt_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='Python Marks:').grid(row=5, column=0, padx=5, pady=5)
python_entry = tk.Entry(add_marks_frame)
python_entry.grid(row=5, column=1, padx=5, pady=5)

tk.Label(add_marks_frame, text='SEPD Marks:').grid(row=6, column=0, padx=5, pady=5)
sepd_entry = tk.Entry(add_marks_frame)
sepd_entry.grid(row=6, column=1, padx=5, pady=5)

add_button = tk.Button(add_marks_frame, text='Add Marks', command=add_marks)
add_button.grid(row=7, columnspan=2, padx=5, pady=10)

# View All Data Frame
view_all_frame = tk.LabelFrame(add_view_tab, text='View All Data')
view_all_frame.pack(padx=10, pady=10, fill='both', expand=True, anchor='center')

view_all_button = tk.Button(view_all_frame, text='View All Data', command=fetch_student_data)
view_all_button.pack(padx=10, pady=10)

# View Individual Data Frame
view_individual_frame = tk.LabelFrame(add_view_tab, text='View Individual Data')
view_individual_frame.pack(padx=10, pady=10, fill='both', expand=True, anchor='center')

tk.Label(view_individual_frame, text='Roll Number:').grid(row=0, column=0, padx=5, pady=5)
roll_view_entry = tk.Entry(view_individual_frame)
roll_view_entry.grid(row=0, column=1, padx=5, pady=5)

view_individual_button = tk.Button(view_individual_frame, text='View Individual Data', command=fetch_individual_data)
view_individual_button.grid(row=1, columnspan=2, padx=5, pady=10)

# New tab for OTP verification and PDF generation
otp_pdf_tab = tk.Frame(notebook)
notebook.add(otp_pdf_tab, text='Generate PDF')

# OTP and PDF Frame
otp_pdf_frame = tk.LabelFrame(otp_pdf_tab, text='Generate PDF')
otp_pdf_frame.pack(padx=10, pady=10, fill='both', expand=True, anchor='center')

tk.Label(otp_pdf_frame, text='Enter Roll Number:').grid(row=0, column=0, padx=5, pady=5)
roll_pdf_entry = tk.Entry(otp_pdf_frame)
roll_pdf_entry.grid(row=0, column=1, padx=5, pady=5)

pdf_button = tk.Button(otp_pdf_frame, text='Generate PDF', command=generate_pdf)
pdf_button.grid(row=1, columnspan=2, padx=5, pady=10)

# Start GUI main loop
root.mainloop()

# Close SQLite connection when the application closes
conn.close()
