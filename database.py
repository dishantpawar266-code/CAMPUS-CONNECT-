import mysql.connector
from mysql.connector import Error
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_connection():
def get_connection():

    st.write("🔥 NEW DATABASE.PY RUNNING")

    if "DB_HOST" in st.secrets:
        st.write("🔥 DB_HOST SECRET FOUND")
        st.write("🔥 HOST:", st.secrets["DB_HOST"])

    else:
        st.write("❌ DB_HOST SECRET NOT FOUND")

    try:
        ...

    try:
        # Streamlit Cloud / TiDB Cloud
        if hasattr(st, "secrets") and "DB_HOST" in st.secrets:

            conn = mysql.connector.connect(
                host=st.secrets["DB_HOST"],
                port=int(st.secrets.get("DB_PORT", 4000)),
                user=st.secrets["DB_USER"],
                password=st.secrets["DB_PASSWORD"],
                database=st.secrets["DB_NAME"],
                ssl_ca=st.secrets.get("DB_SSL_CA"),
                ssl_verify_cert=True,
                ssl_verify_identity=True
            )

        # Local computer
        else:

            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "campusconnect")
            )

        return conn

    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None
