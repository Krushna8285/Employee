CREATE DATABASE IF NOT EXISTS employee_db;

USE employee_db;


-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    fullname VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL

);


-- =====================================================
-- EMPLOYEES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS employees (

    id INT AUTO_INCREMENT PRIMARY KEY,

    emp_id VARCHAR(50) NOT NULL UNIQUE,

    fullname VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL,

    phone VARCHAR(20),

    department VARCHAR(100),

    designation VARCHAR(100),

    salary DECIMAL(10,2),

    joining_date DATE,

    photo VARCHAR(255)

);


-- =====================================================
-- ATTENDANCE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS attendance (

    id INT AUTO_INCREMENT PRIMARY KEY,

    employee_id INT NOT NULL,

    attendance_date DATE NOT NULL,

    status ENUM('Present', 'Absent', 'Leave') NOT NULL,

    FOREIGN KEY (employee_id)
        REFERENCES employees(id)
        ON DELETE CASCADE,

    UNIQUE(employee_id, attendance_date)

);