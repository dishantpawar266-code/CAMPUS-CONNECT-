import streamlit as st
import os
from database import get_connection
import mysql.connector
from datetime import datetime

# Upload path for student submissions
SUBMISSION_DIR = os.path.join("uploads", "submissions")
if not os.path.exists(SUBMISSION_DIR):
    os.makedirs(SUBMISSION_DIR)

def show_assignments_page():
    st.title("📝 Assignments Portal")
    st.caption("View pending assignments and submit your completed work.")

    tab1, tab2 = st.tabs(["📌 Pending Assignments", "📤 Submit Assignment"])

    # ---------------- TAB 1: VIEW ASSIGNMENTS ---------------- #
    with tab1:
        st.subheader("Available Assignments")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM assignments ORDER BY due_date ASC")
            assignments_list = cursor.fetchall()
            cursor.close()
            conn.close()

            if not assignments_list:
                st.info("No active assignments found.")
            else:
                for assign in assignments_list:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {assign['title']}")
                            st.write(f"**Description:** {assign['description']}")
                            st.caption(f"Posted by: **{assign['uploaded_by']}** | Due Date: **{assign['due_date']}**")
                        with col2:
                            if assign['file_path'] and os.path.exists(assign['file_path']):
                                with open(assign['file_path'], "rb") as file:
                                    st.download_button(
                                        label="⬇️ Problem File",
                                        data=file,
                                        file_name=os.path.basename(assign['file_path']),
                                        key=f"asg_dl_{assign['id']}",
                                        use_container_width=True
                                    )

    # ---------------- TAB 2: SUBMIT WORK ---------------- #
    with tab2:
        st.subheader("Submit Your Solution")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, title FROM assignments")
            assign_options = {row['title']: row['id'] for row in cursor.fetchall()}
            cursor.close()
            conn.close()

            if not assign_options:
                st.warning("No assignments available for submission.")
            else:
                with st.form("submit_assignment_form", clear_on_submit=True):
                    selected_title = st.selectbox("Select Assignment", list(assign_options.keys()))
                    submitted_file = st.file_uploader("Upload Solution (PDF/DOCX)", type=["pdf", "docx", "zip"])
                    
                    submit_btn = st.form_submit_button("Submit Assignment", use_container_width=True)

                    if submit_btn:
                        if not submitted_file:
                            st.error("Please attach a file before submitting.")
                        else:
                            assign_id = assign_options[selected_title]
                            user_name = st.session_state.get("name", "Student")

                            # Save file locally
                            file_name = f"{user_name.replace(' ', '_')}_{submitted_file.name}"
                            save_path = os.path.join(SUBMISSION_DIR, file_name)
                            
                            with open(save_path, "wb") as f:
                                f.write(submitted_file.getbuffer())

                            # Insert into database
                            conn = get_connection()
                            if conn:
                                cursor = conn.cursor()
                                query = """
                                    INSERT INTO submissions (assignment_id, submitted_by, file_path)
                                    VALUES (%s, %s, %s)
                                """
                                cursor.execute(query, (assign_id, user_name, save_path))
                                conn.commit()
                                cursor.close()
                                conn.close()

                                st.success("Assignment submitted successfully!")
                                st.rerun()