import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if available)
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "3251")
DB_NAME = os.getenv("DB_NAME", "campusconnect")

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Database Connection Failed: {e}")
        return None