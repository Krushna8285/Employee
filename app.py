
import os
import re
from datetime import date
from flask import (Flask,render_template,request,redirect,session,flash,send_from_directory)
from werkzeug.utils import secure_filename
from werkzeug.security import (generate_password_hash,check_password_hash)
from db import get_connection


app = Flask(__name__)

app.secret_key = "employee123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}


# =====================================================
# UPLOADED PHOTO
# =====================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# =====================================================
# REGISTER PAGE
# =====================================================

@app.route("/register", methods=["GET"])
def register_page():

    return render_template("register.html")


# =====================================================
# REGISTER USER
# =====================================================

@app.route("/register", methods=["POST"])
def register():

    fullname = request.form["fullname"]
    email = request.form["email"]
    password = request.form["password"]

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already registered!", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        sql = """
        INSERT INTO users(fullname, email, password)
        VALUES(%s, %s, %s)
        """

        cursor.execute(
            sql,
            (fullname, email, hashed_password)
        )

        conn.commit()

        flash("Registration Successful!", "success")

        return redirect("/login")

    except Exception as e:

        print("REGISTER ERROR:", e)

        if conn:
            conn.rollback()

        flash(
            "Registration failed. Please try again!",
            "danger"
        )

        return redirect("/register")

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =====================================================
# LOGIN PAGE
# =====================================================
@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET"])
def login_page():

    return render_template("login.html")


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    
    email = request.form["email"]
    password = request.form["password"]

    

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Search user by email
        sql = """
        SELECT * FROM users
        WHERE email=%s
        """

        cursor.execute(
            sql,
            (email,)
        )

        user = cursor.fetchone()

        # Check password
        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user"] = user["fullname"]

            return redirect("/dashboard")

        flash(
            "Invalid Email or Password!",
            "danger"
        )

        return redirect("/login")

    except Exception as e:

        print("LOGIN ERROR:", e)

        flash(
            "Login failed. Please try again!",
            "danger"
        )

        return redirect("/login")

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    # Total Employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    # Present Today
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = CURDATE()
        AND status = 'Present'
    """)
    present_today = cursor.fetchone()[0]

    # Absent Today
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = CURDATE()
        AND status = 'Absent'
    """)
    absent_today = cursor.fetchone()[0]

    # Leave Today
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = CURDATE()
        AND status = 'Leave'
    """)
    leave_today = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        leave_today=leave_today
    )


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template("500.html"), 500


# =====================================================
# ADD EMPLOYEE PAGE
# =====================================================

@app.route("/add_employee")
def add_employee():

    if "user" not in session:
        return redirect("/login")

    return render_template("add_employee.html")


# =====================================================
# SAVE EMPLOYEE
# =====================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/save_employee", methods=["POST"])
def save_employee():

    if "user" not in session:
        return redirect("/login")

    # ==========================================
    # GET FORM DATA
    # ==========================================

    emp_id = request.form["emp_id"].strip()
    fullname = request.form["fullname"].strip()
    email = request.form["email"].strip().lower()
    phone = request.form["phone"].strip()
    department = request.form["department"].strip()
    designation = request.form["designation"].strip()
    salary = request.form["salary"].strip()
    joining_date = request.form["joining_date"].strip()


    # ==========================================
    # EMAIL VALIDATION
    # ==========================================

    email_pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    if not re.match(email_pattern, email):

        flash(
            "Please enter a valid email address!",
            "danger"
        )

        return redirect("/add_employee")


    # ==========================================
    # PHOTO
    # ==========================================

    photo = request.files.get("photo")

    filename = ""


    if photo and photo.filename != "":

        if not allowed_file(photo.filename):

            flash(
                "Only JPG, JPEG, PNG and GIF images are allowed!",
                "danger"
            )

            return redirect("/add_employee")


        filename = secure_filename(photo.filename)


        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )


    conn = None
    cursor = None


    try:

        conn = get_connection()
        cursor = conn.cursor(buffered=True)


        # ==========================================
        # CHECK DUPLICATE EMPLOYEE ID
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE emp_id=%s
            """,
            (emp_id,)
        )

        existing_employee = cursor.fetchone()


        if existing_employee:

            flash(
                "Employee ID already exists!",
                "danger"
            )

            return redirect("/add_employee")


        # ==========================================
        # CHECK DUPLICATE EMAIL
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE LOWER(email)=LOWER(%s)
            """,
            (email,)
        )

        existing_email = cursor.fetchone()


        if existing_email:

            flash(
                "Email already exists!",
                "danger"
            )

            return redirect("/add_employee")

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE phone=%s
            """,
            (phone,)
        )
        existing_phone = cursor.fetchone()
        if existing_phone:
            flash(
                "phone number already exists!",
                "danger"
            )
            return redirect("/add_employee")


        # ==========================================
        # INSERT EMPLOYEE
        # ==========================================

        sql = """
        INSERT INTO employees
        (
            emp_id,
            fullname,
            email,
            phone,
            department,
            designation,
            salary,
            joining_date,
            photo
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """


        values = (
            emp_id,
            fullname,
            email,
            phone,
            department,
            designation,
            salary,
            joining_date,
            filename
        )


        cursor.execute(
            sql,
            values
        )


        conn.commit()


        flash(
            "Employee Added Successfully!",
            "success"
        )


        return redirect("/employees")


    except Exception as e:

        if conn:
            conn.rollaback()
        print("SAVE EMPLOYEE ERROR:", repr(e), flush=True)


        flash(f"Database Error: {str(e)}", "danger")

        
        return redirect("/add_employee")


    finally:

        if cursor:

            cursor.close()


        if conn:

            conn.close()

# =====================================================
# EMPLOYEE PROFILE
# =====================================================

@app.route("/employee/<int:id>")
def employee_profile(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Employee details
    cursor.execute(
        "SELECT * FROM employees WHERE id=%s",
        (id,)
    )

    employee = cursor.fetchone()

    if employee is None:
        cursor.close()
        conn.close()
        return "Employee Not Found"

    # Employee attendance history
    cursor.execute(
        """
        SELECT attendance_date, status
        FROM attendance
        WHERE employee_id=%s
        ORDER BY attendance_date DESC
        """,
        (id,)
    )

    attendance = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "employee_profile.html",
        employee=employee,
        attendance=attendance
    )


# =====================================================
# ATTENDANCE PAGE
# =====================================================

@app.route("/attendance")
def attendance():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        attendance.id,
        employees.emp_id,
        employees.fullname,
        employees.department,
        attendance.attendance_date,
        attendance.status
    FROM attendance
    JOIN employees
        ON attendance.employee_id = employees.id
    ORDER BY attendance.attendance_date DESC
    """

    cursor.execute(sql)

    attendance_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "attendance.html",
        attendance=attendance_data
    )

# =====================================================
# MARK ATTENDANCE PAGE
# =====================================================

@app.route("/mark_attendance")
def mark_attendance():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, emp_id, fullname FROM employees")

    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "mark_attendance.html",
        employees=employees
    )

# =====================================================
# SAVE ATTENDANCE
# =====================================================

@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    if "user" not in session:
        return redirect("/login")

    employee_id = request.form.get("employee_id", "").strip()
    attendance_date = request.form.get("attendance_date", "").strip()
    status = request.form.get("status", "").strip()

    conn = None
    cursor = None

    try:

        # ==========================================
        # BASIC VALIDATION
        # ==========================================

        if not employee_id or not attendance_date or not status:

            flash(
                "All attendance fields are required!",
                "danger"
            )

            return redirect("/mark_attendance")


        # ==========================================
        # VALID STATUS
        # ==========================================

        allowed_status = {
            "Present",
            "Absent",
            "Leave"
        }

        if status not in allowed_status:

            flash(
                "Invalid attendance status!",
                "danger"
            )

            return redirect("/mark_attendance")


        # ==========================================
        # FUTURE DATE CHECK
        # ==========================================

        if attendance_date > str(date.today()):

            flash(
                "Future date attendance is not allowed!",
                "danger"
            )

            return redirect("/mark_attendance")


        # ==========================================
        # DATABASE CONNECTION
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor(
            buffered=True
        )


        # ==========================================
        # CHECK EMPLOYEE EXISTS
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE id=%s
            """,
            (employee_id,)
        )

        employee = cursor.fetchone()

        if not employee:

            flash(
                "Employee not found!",
                "danger"
            )

            return redirect("/mark_attendance")


        # ==========================================
        # CHECK DUPLICATE ATTENDANCE
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM attendance
            WHERE employee_id=%s
            AND attendance_date=%s
            """,
            (
                employee_id,
                attendance_date
            )
        )

        existing = cursor.fetchone()

        if existing:

            flash(
                "Attendance already exists for this employee on this date!",
                "warning"
            )

            return redirect("/mark_attendance")


        # ==========================================
        # SAVE ATTENDANCE
        # ==========================================

        cursor.execute(
            """
            INSERT INTO attendance
            (
                employee_id,
                attendance_date,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                employee_id,
                attendance_date,
                status
            )
        )


        # ==========================================
        # COMMIT
        # ==========================================

        conn.commit()


        flash(
            "Attendance Saved Successfully!",
            "success"
        )


        return redirect("/attendance")


    except Exception as e:

        print(
            "ATTENDANCE ERROR:",
            e
        )

        if conn:

            conn.rollback()


        flash(
            "Error while saving attendance!",
            "danger"
        )


        return redirect("/mark_attendance")


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()

# =====================================================
# DELETE ATTENDANCE
# =====================================================

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):

    if "user" not in session:
        return redirect("/login")

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            """
            SELECT id
            FROM attendance
            WHERE id=%s
            """,
            (id,)
        )

        attendance = cursor.fetchone()

        if not attendance:

            flash(
                "Attendance record not found!",
                "danger"
            )

            return redirect("/attendance")


        cursor.execute(
            """
            DELETE FROM attendance
            WHERE id=%s
            """,
            (id,)
        )

        conn.commit()

        flash(
            "Attendance Deleted Successfully!",
            "success"
        )

        return redirect("/attendance")


    except Exception as e:

        print("DELETE ATTENDANCE ERROR:", e)

        if conn:
            conn.rollback()

        flash(
            "Error while deleting attendance!",
            "danger"
        )

        return redirect("/attendance")


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
# =====================================================
# EMPLOYEE LIST
# =====================================================

@app.route("/employees")
def employees():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM employees"
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "employees.html",
        employees=data
    )


# =====================================================
# EDIT EMPLOYEE
# =====================================================

@app.route("/edit/<int:id>")
def edit_employee(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM employees WHERE id=%s",
        (id,)
    )

    employee = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )


# =====================================================
# UPDATE EMPLOYEE
# =====================================================


@app.route("/update_employee/<int:id>", methods=["POST"])
def update_employee(id):

    if "user" not in session:
        return redirect("/login")

    emp_id = request.form.get("emp_id", "").strip()
    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()
    salary = request.form.get("salary", "").strip()
    joining_date = request.form.get("joining_date", "").strip()

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(buffered=True)

        # ==========================================
        # CHECK EMPLOYEE EXISTS
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE id=%s
            """,
            (id,)
        )

        employee = cursor.fetchone()

        if not employee:

            flash(
                "Employee not found!",
                "danger"
            )

            return redirect("/employees")


        # ==========================================
        # EMAIL VALIDATION
        # ==========================================

        email_pattern = (
            r"^[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}$"
        )

        if not re.match(email_pattern, email):

            flash(
                "Please enter a valid email address!",
                "danger"
            )

            return redirect(f"/edit/{id}")


        # ==========================================
        # PHONE VALIDATION
        # ==========================================

        if not phone.isdigit() or len(phone) != 10:

            flash(
                "Phone number must contain exactly 10 digits!",
                "danger"
            )

            return redirect(f"/edit/{id}")


        # ==========================================
        # DUPLICATE EMPLOYEE ID
        # Exclude current employee
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE emp_id=%s
            AND id!=%s
            """,
            (
                emp_id,
                id
            )
        )

        existing_emp_id = cursor.fetchone()

        if existing_emp_id:

            flash(
                "Employee ID already exists!",
                "danger"
            )

            return redirect(f"/edit/{id}")


        # ==========================================
        # DUPLICATE EMAIL
        # Exclude current employee
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE LOWER(email)=LOWER(%s)
            AND id!=%s
            """,
            (
                email,
                id
            )
        )

        existing_email = cursor.fetchone()

        if existing_email:

            flash(
                "Email already exists!",
                "danger"
            )

            return redirect(f"/edit/{id}")


        # ==========================================
        # DUPLICATE PHONE
        # Exclude current employee
        # ==========================================

        cursor.execute(
            """
            SELECT id
            FROM employees
            WHERE phone=%s
            AND id!=%s
            """,
            (
                phone,
                id
            )
        )

        existing_phone = cursor.fetchone()

        if existing_phone:

            flash(
                "Phone number already exists!",
                "danger"
            )

            return redirect(f"/edit/{id}")


        # ==========================================
        # UPDATE EMPLOYEE
        # ==========================================

        cursor.execute(
            """
            UPDATE employees
            SET
                emp_id=%s,
                fullname=%s,
                email=%s,
                phone=%s,
                department=%s,
                designation=%s,
                salary=%s,
                joining_date=%s
            WHERE id=%s
            """,
            (
                emp_id,
                fullname,
                email,
                phone,
                department,
                designation,
                salary,
                joining_date,
                id
            )
        )

        conn.commit()

        flash(
            "Employee Updated Successfully!",
            "success"
        )

        return redirect("/employees")


    except Exception as e:

        print(
            "UPDATE EMPLOYEE ERROR:",
            e
        )

        if conn:
            conn.rollback()

        flash(
            "Error while updating employee!",
            "danger"
        )

        return redirect(f"/edit/{id}")


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =====================================================
# DELETE EMPLOYEE
# =====================================================

@app.route("/delete/<int:id>")
def delete_employee(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM employees WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Employee Deleted Successfully!")

    return redirect("/employees")


# =====================================================
# SEARCH EMPLOYEE
# =====================================================

@app.route("/search")
def search():

    if "user" not in session:
        return redirect("/login")

    keyword = request.args.get(
        "keyword",
        ""
    )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM employees
    WHERE fullname LIKE %s
       OR department LIKE %s
       OR designation LIKE %s
    """

    value = "%" + keyword + "%"

    cursor.execute(
        sql,
        (value, value, value)
    )

    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "employees.html",
        employees=employees
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully!", "success")

    return redirect("/login")


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run( host="0.0.0.0", port=5000, debug=True)