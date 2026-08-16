# Employee Management System

A web-based Employee Management System developed using Python Flask and MySQL.

## Features

### Authentication
- User Registration
- User Login
- Password Hashing
- Logout
- Session Management

### Employee Management
- Add Employee
- View Employees
- Search Employees
- Edit Employee
- Delete Employee
- Employee Profile
- Employee Photo Upload

### Validation
- Duplicate Employee ID validation
- Duplicate Email validation
- Duplicate Phone validation
- Email format validation
- 10-digit phone validation
- Image file validation

### Attendance Management
- Mark Attendance
- Present / Absent / Leave
- Prevent duplicate attendance
- Prevent future-date attendance
- Edit Attendance
- Delete Attendance
- Attendance List

### Dashboard
- Total Employees
- Present Today
- Absent Today
- Leave Today

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- Bootstrap 5
- JavaScript
- Jinja2

## Project Structure

```text
Employee_Management_System/
│
├── app.py
├── db.py
├── requirements.txt
├── README.md
│
├── database/
│   └── database.sql
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── employees.html
│   ├── add_employee.html
│   ├── edit_employee.html
│   ├── employee_profile.html
│   ├── attendance.html
│   ├── mark_attendance.html
│   ├── edit_attendance.html
│   └── attendance_list.html
│
└── uploads/