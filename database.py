import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="3251",
            database="campusconnect",
            port=3306
        )

        if connection.is_connected():
            return connection

    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None
