import mysql.connector
from mysql.connector import Error
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ==============================
# DATABASE CONFIGURATION
# ==============================

# Check if Streamlit Cloud secrets are available
if "mysql" in st.secrets:

    # TiDB Cloud / Streamlit Cloud
    DB_HOST = st.secrets["mysql"]["host"]
    DB_PORT = int(st.secrets["mysql"]["port"])
    DB_USER = st.secrets["mysql"]["username"]
    DB_PASSWORD = st.secrets["mysql"]["password"]
    DB_NAME = st.secrets["mysql"]["database"]

    IS_CLOUD = True

else:

    # Local MySQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "campusconnect")

    IS_CLOUD = False


# ==============================
# DATABASE CONNECTION
# ==============================

def get_connection():

    try:

        if IS_CLOUD:

            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,

                # TiDB Cloud SSL
                ssl_verify_cert=True,
                ssl_verify_identity=True
            )

        else:

            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

        if conn.is_connected():
            return conn

    except Error as e:

        print(f"Database Connection Failed: {e}")

        # Show error in Streamlit Cloud
        if IS_CLOUD:
            st.error(f"Database Connection Failed: {e}")

        return None

    return None