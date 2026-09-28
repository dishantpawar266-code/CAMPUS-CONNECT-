import mysql.connector
from mysql.connector import Error
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ==============================
# DATABASE CONFIGURATION
# ==============================

try:
    # Streamlit Cloud
    DB_HOST = st.secrets["mysql"]["host"]
    DB_PORT = int(st.secrets["mysql"]["port"])
    DB_USER = st.secrets["mysql"]["username"]
    DB_PASSWORD = st.secrets["mysql"]["password"]
    DB_NAME = st.secrets["mysql"]["database"]

except Exception:
    # Local computer
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "campusconnect")


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl_verify_cert=True,
            ssl_verify_identity=True
        )

        if conn.is_connected():
            return conn

    except Error as e:
        print(f"Database Connection Failed: {e}")
        return None
