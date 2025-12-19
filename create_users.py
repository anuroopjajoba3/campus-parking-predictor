import bcrypt
import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Verizonsam@9896',
    database='parking_db'
)
cursor = conn.cursor()

# Delete existing users
cursor.execute("DELETE FROM users")

# Create admin user
admin_password = "admin123"
admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor.execute("""
    INSERT INTO users (email, password_hash, full_name, role) 
    VALUES (%s, %s, %s, %s)
""", ('admin@unh.edu', admin_hash, 'Admin User', 'admin'))

print(f"✅ Admin created: admin@unh.edu / {admin_password}")

# Create student user
student_password = "user123"
student_hash = bcrypt.hashpw(student_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor.execute("""
    INSERT INTO users (email, password_hash, full_name, role) 
    VALUES (%s, %s, %s, %s)
""", ('student@unh.edu', student_hash, 'Test Student', 'user'))

print(f"✅ Student created: student@unh.edu / {student_password}")

# Create faculty user
faculty_password = "user123"
faculty_hash = bcrypt.hashpw(faculty_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor.execute("""
    INSERT INTO users (email, password_hash, full_name, role) 
    VALUES (%s, %s, %s, %s)
""", ('faculty@unh.edu', faculty_hash, 'Test Faculty', 'user'))

print(f"✅ Faculty created: faculty@unh.edu / {faculty_password}")

conn.commit()
cursor.close()
conn.close()

print("\n🎉 All users created successfully!")
print("\nLogin credentials:")
print("Admin:   admin@unh.edu / admin123")
print("Student: student@unh.edu / user123")
print("Faculty: faculty@unh.edu / user123")
