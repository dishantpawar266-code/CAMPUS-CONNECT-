import datetime
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


def show_doubt_forum_page():
    st.title("💬 Student Doubt Forum")
    st.caption(
        "Ask questions, clear your concepts, and view answers from faculty members."
    )
    st.markdown("---")

    user_name = st.session_state.get(
        "name", st.session_state.get("username", "DISHANT H PAWAR")
    )

    # --- Section: Post a New Doubt ---
    with st.expander("➕ Ask a New Doubt", expanded=True):
        with st.form("new_doubt_form", clear_on_submit=True):
            subject = st.text_input(
                "Subject / Course Name",
                placeholder="e.g. Artificial Intelligence & Machine Learning",
            )
            question = st.text_area(
                "Your Question / Doubt",
                placeholder="Describe your doubt clearly...",
            )
            submitted = st.form_submit_button("Post Doubt", type="primary")

            if submitted:
                if subject.strip() and question.strip():
                    conn = get_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            # Ensure table exists with subject column if not present
                            cursor.execute(
                                """
                                CREATE TABLE IF NOT EXISTS student_doubts (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    student_name VARCHAR(150) NOT NULL,
                                    subject VARCHAR(150),
                                    question TEXT NOT NULL,
                                    reply TEXT,
                                    status VARCHAR(50) DEFAULT 'Pending',
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """
                            )
                            cursor.execute(
                                """
                                INSERT INTO student_doubts (student_name, subject, question, status) 
                                VALUES (%s, %s, %s, 'Pending')
                            """,
                            (
                                user_name,
                                subject.strip(),
                                question.strip(),
                            ),
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(
                                "✅ Your doubt has been posted successfully and sent to faculty!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(
                                f"Database error while posting doubt: {e}"
                            )
                    else:
                        st.error(
                            "Database connection failed. Please check your DB settings."
                        )
                else:
                    st.warning("Please fill in both subject and question.")

    st.markdown("### 📋 Community Doubts & Solutions")

    # --- Section: View All Doubts from student_doubts table ---
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student_doubts ORDER BY created_at DESC")
            doubts = cursor.fetchall()
            cursor.close()
            conn.close()

            if not doubts:
                st.info(
                    "No doubts posted yet. Be the first one to ask a question!"
                )
            else:
                for doubt in doubts:
                    with st.container(border=True):
                        status = doubt.get("status", "Pending")
                        status_badge = (
                            "✅ Resolved"
                            if status == "Resolved"
                            else "⏳ Pending"
                        )

                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(
                                f"**Asked by:** {doubt.get('student_name', 'Student')} | **Subject:** `{doubt.get('subject', 'General')}`"
                            )
                        with col2:
                            st.markdown(f"**Status:** {status_badge}")

                        st.markdown(f"❓ **Question:** {doubt.get('question')}")
                        st.caption(f"Posted on: {doubt.get('created_at', '')}")

                        # Display Faculty Reply directly from student_doubts record
                        reply_text = doubt.get("reply")
                        if reply_text:
                            st.markdown("---")
                            st.success(f"**💡 Faculty Response:** {reply_text}")
                        else:
                            st.info("⏳ Waiting for faculty response...")
        except Exception as e:
            st.error(
                f"Could not load doubts from database. Make sure the 'student_doubts' table exists. Error: {e}"
            )
