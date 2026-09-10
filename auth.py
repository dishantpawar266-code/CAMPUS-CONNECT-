import mysql.connector
from database import get_connection

def login_user(role, email, password):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        table = "students" if role.strip().title() == "Student" else "faculty"
        clean_email = email.strip()

        cursor.execute(
            f"SELECT * FROM {table} WHERE email = %s AND password = %s",
            (clean_email, password)
        )

        user = cursor.fetchone()
        return user

    except mysql.connector.Error as err:
        print(f"Database Query Error: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def register_student(full_name, email, password, branch, year):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            return False, "Database connection failed."

        cursor = conn.cursor()
        clean_email = email.strip()

        # Check if email already exists
        cursor.execute("SELECT id FROM students WHERE email = %s", (clean_email,))
        if cursor.fetchone():
            return False, "This email is already registered."

        # Insert student record
        query = """
            INSERT INTO students (full_name, email, password, branch, year) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (full_name.strip(), clean_email, password, branch, year))
        conn.commit()

        return True, "Account created successfully! You can now log in."

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return False, f"Database error: {err}"

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()