import sqlite3

def create_database():
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        credits INTEGER NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        courses = [
            ("Java", 4),
            ("Python", 3),
            ("SQL Fundamentals", 3),
            ("Web Devlopment", 4),
            ("C++", 4)
        ]
        cursor.executemany("INSERT INTO courses (course_name, credits) VALUES (?, ?)",courses)
    
    conn.commit()
    conn.close()
    
def add_student():
    print("\n----Add Student----")
    
    name = input("Enter student name:").strip()
    if not name:
        print("Name cannot be empty !")
        return
    
    try:
        age = int(input("Enter student age:"))
        if age<=16:
            print("Age must be greater than 16")
            return
    except ValueError:
        print("Age must be a number")
        return
    
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()
    print("Student added successfully!")
    

def enroll_student():
    print("\n---- Enroll Student ----")
    
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()

    print("\nStudents:")
    cursor.execute("SELECT * FROM students")
    for s in cursor.fetchall():
        print(f"ID: {s[0]} | Name: {s[1]} | Age: {s[2]}")

    print("\nCourses:")
    cursor.execute("SELECT * FROM courses")
    for c in cursor.fetchall():
        print(f"ID: {c[0]} | Course: {c[1]} | Credits: {c[2]}")

    student_id = int(input("\nEnter Student ID to enroll: "))

    course_ids = input("Enter Course IDs (comma separated): ").split(",")

    for cid in course_ids:
        cid = int(cid.strip())
        cursor.execute("SELECT * FROM enrollments WHERE student_id=? AND course_id=?", (student_id, cid))
        exists = cursor.fetchone()

        if exists:
            print(f"Student {student_id} is already enrolled in course {cid}")
        else:
            cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, cid))
            print(f"Enrolled student {student_id} in course {cid}")

    conn.commit()

    print("\n----- Student Enrollments -----")
    cursor.execute("""
    SELECT s.name, GROUP_CONCAT(c.course_name, ', ')
    FROM enrollments e
    JOIN students s ON e.student_id = s.id
    JOIN courses c ON e.course_id = c.id
    GROUP BY s.id
    """)
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")

    conn.close()
    
     
def update_student():
    print("\n----Update Student----")
    
    try:
        student_id = int(input("Enter student id to update:"))
    except ValueError:
        print("Invalid ID")
        return
    
    new_name = input("Enter new name:").strip()
    if not new_name:
        print("Name cannot be empty")
        return
        
    try:
        new_age = int(input("Enter age:"))
        if new_age <= 16:
            print("Age must be greater than 16")
            return
    except ValueError:
        print("Age must be number")
        return
    
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    if not cursor.fetchone():
        print("Student ID not found!")
        conn.close()
        return
    
    cursor.execute("UPDATE students SET name=?, age=? WHERE id=?",(new_name, new_age, student_id))
    
    cursor.execute("""
    SELECT c.id, c.course_name
    FROM enrollments e
    JOIN courses c ON e.course_id = c.id
    WHERE e.student_id = ?
    """,(student_id,))
    current_course = cursor.fetchall()
    
    if current_course:
        print("\nCurrent courses")
        for c in current_course:
            print(f"{c[0]} - {c[1]}")
    else:
        print("\nStudent is not enrolled in any course yet")
            
    print("\nAvailable courses")
    cursor.execute("SELECT * FROM courses")
    all_courses = cursor.fetchall()
    for c in all_courses:
        print(f"{c[0]} - {c[1]}")
        
    new_course_id = input("Enter new course ID to enroll: ").strip()
    if new_course_id:
        course_ids = [int(cid.strip()) for cid in new_course_id.split(",")]
        cursor.execute("DELETE FROM enrollments WHERE student_id =?",(student_id,))
        for cid in course_ids:
            cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",(student_id,cid))
    
    conn.commit()
    conn.close()
    print("Student details and course updated successfully!")
    
    
def delete_student():
    print("\n----Delete Student----")
    
    try:
        student_id = int(input("Enter student ID to delete:"))
    except ValueError:
        print("Invalid ID")
        return
    
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    if not cursor.fetchone():
        print("Student ID not found!")
        conn.close()
        return
    
    cursor.execute("DELETE FROM enrollments WHERE student_id=?",(student_id,))
    cursor.execute("DELETE FROM students WHERE id=?",(student_id,))
    conn.commit()
    conn.close()
    print("Student deleted successfully!")
    

def view_students():
    print("\n--- All Students with Courses ---")
    conn = sqlite3.connect("Student_Management_System.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.name, s.age,
           COALESCE(GROUP_CONCAT(c.course_name, ', '), 'Not Enrolled') AS courses
    FROM students s
    LEFT JOIN enrollments e ON s.id = e.student_id
    LEFT JOIN courses c ON e.course_id = c.id
    GROUP BY s.id
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Age: {row[2]} | Courses: {row[3]}")


create_database()     

while True:
    print("\n====== Student Management System ======")
    print("1. Add Student")
    print("2. Enroll Student")
    print("3. Update Student")
    print("4. Delete Student")
    print("5. View Students")
    print("6. Exit")

    choice = input("Enter choice (1-6): ")

    if choice == "1":
        add_student()
    elif choice == "2":
        enroll_student()
    elif choice == "3":
        update_student()
    elif choice == "4":
        delete_student()
    elif choice == "5":
        view_students()
    elif choice == "6":
        print("Exiting program...")
        break
    else:
        print("Invalid choice, try again!")