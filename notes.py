import datetime
import os
import mysql.connector
import streamlit as st


# Database Connection Helper
def get_connection():
    try:
        from database import get_connection as conn

        return conn()
    except ImportError:
        try:
            from db import get_connection as conn

            return conn()
        except ImportError:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="3251",
                database="campusconnect",
            )


def ensure_notes_schema(conn):
    """Ensures notes table exists with the correct columns."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                file_path VARCHAR(512),
                uploaded_by VARCHAR(100),
                role VARCHAR(50) DEFAULT 'Student',
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT
            )
        """)
        conn.commit()

        # Safely add missing columns if table already existed
        for col_def in [
            ("file_path", "VARCHAR(512)"),
            ("role", "VARCHAR(50) DEFAULT 'Student'"),
            (
                "upload_date",
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            ),
            ("user_id", "INT"),
        ]:
            try:
                cursor.execute(
                    f"ALTER TABLE notes ADD COLUMN {col_def[0]} {col_def[1]}"
                )
                conn.commit()
            except Exception:
                pass  # Column already exists

        cursor.close()
    except Exception as e:
        st.error(f"Schema Error: {e}")


def show_notes_page():
    st.title("📚 Notes Directory")
    st.caption(
        "Upload and access subject notes shared by students and faculty."
    )
    st.markdown("---")

    conn = get_connection()
    if conn:
        ensure_notes_schema(conn)
        conn.close()

    tab_view, tab_upload = st.tabs(["📁 View Notes", "📤 Upload Note"])

    # ---------------- 1. VIEW ALL NOTES ---------------- #
    with tab_view:
        st.subheader("📖 Available Study Material")
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM notes ORDER BY id DESC")
                notes_list = cursor.fetchall()
                cursor.close()

                if not notes_list:
                    st.info("ℹ️ No study materials available yet.")
                else:
                    for note in notes_list:
                        with st.container(border=True):
                            st.markdown(
                                f"**📌 {note.get('title', 'Note')}**"
                                f" (`{note.get('subject', 'General')}`)"
                            )
                            st.caption(
                                f"Uploaded by: {note.get('uploaded_by', 'User')} | Date: {note.get('upload_date', 'N/A')}"
                            )

                            f_path = note.get("file_path")
                            if f_path and os.path.exists(f_path):
                                with open(f_path, "rb") as f_obj:
                                    st.download_button(
                                        "📥 Download File",
                                        data=f_obj,
                                        file_name=os.path.basename(f_path),
                                        key=f"view_dl_{note['id']}",
                                    )
                            elif f_path:
                                st.warning(
                                    f"⚠️ File path recorded in database, but file is missing on server: {f_path}"
                                )
            except Exception as e:
                st.error(f"Database Error: {e}")
            finally:
                conn.close()

    # ---------------- 2. UPLOAD NOTE & MY UPLOADS ---------------- #
    with tab_upload:
        st.subheader("Upload New Study Material")

        with st.form("student_upload_note_form", clear_on_submit=True):
            title = st.text_input("Note Title (e.g. Unit 1 Vector Calculus)")
            subject = st.text_input("Subject Name (e.g. Engineering Maths)")
            uploaded_file = st.file_uploader(
                "Choose a file (PDF, TXT, DOCX, PNG, JPG, PPTX)",
                type=["pdf", "txt", "docx", "png", "jpg", "pptx"],
            )
            submitted = st.form_submit_button("Submit & Save", type="primary")

            if submitted:
                if title.strip() and subject.strip() and uploaded_file:
                    student_name = st.session_state.get(
                        "name",
                        st.session_state.get("username", "DISHANT H PAWAR"),
                    )
                    user_id = st.session_state.get("user_id", 1)

                    # Ensure uploads directory exists
                    os.makedirs("uploads", exist_ok=True)
                    safe_filename = uploaded_file.name.replace(" ", "_")
                    file_path = os.path.join("uploads", safe_filename)

                    # Save file locally to disk
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    conn = get_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                INSERT INTO notes (title, subject, file_path, uploaded_by, role, user_id) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    title.strip(),
                                    subject.strip(),
                                    file_path,
                                    student_name,
                                    "Student",
                                    user_id,
                                ),
                            )
                            conn.commit()
                            cursor.close()
                            st.success(
                                "✅ Study material uploaded successfully!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error uploading note: {e}")
                        finally:
                            conn.close()
                else:
                    st.warning("Please fill all fields and attach a file.")

        st.markdown("---")
        st.subheader("📋 My Uploaded Notes")

        current_user_id = st.session_state.get("user_id", 1)
        current_user_name = st.session_state.get(
            "name", st.session_state.get("username", "DISHANT H PAWAR")
        )

        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """
                    SELECT * FROM notes 
                    WHERE uploaded_by = %s OR user_id = %s
                    ORDER BY id DESC
                """,
                    (current_user_name, current_user_id),
                )

                my_notes = cursor.fetchall()
                cursor.close()

                if not my_notes:
                    st.info(
                        "ℹ️ You haven't uploaded any notes yet. Upload one above to see it here!"
                    )
                else:
                    for note in my_notes:
                        with st.container(border=True):
                            col_info, col_del = st.columns([4, 1])

                            with col_info:
                                st.markdown(
                                    f"**📌 {note.get('title', 'Note')}**"
                                )
                                st.caption(
                                    f"Subject: `{note.get('subject')}` | File: `{os.path.basename(note.get('file_path', 'N/A'))}`"
                                )

                            with col_del:
                                if st.button(
                                    "🗑️ Delete",
                                    key=f"del_note_{note['id']}",
                                    type="secondary",
                                    use_container_width=True,
                                ):
                                    del_cursor = conn.cursor()
                                    del_cursor.execute(
                                        "DELETE FROM notes WHERE id = %s",
                                        (note["id"],),
                                    )
                                    conn.commit()
                                    del_cursor.close()
                                    st.success(
                                        "🗑️ Note deleted successfully!"
                                    )
                                    st.rerun()

            except Exception as e:
                st.error(f"Database Error: {e}")
            finally:
                conn.close()