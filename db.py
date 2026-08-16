
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )




# import mysql.connector

# def get_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Krushna@123",
#         database="employee_db"
#     )
    