import datetime
import os
import mysql.connector
import streamlit as st

# --- FOLDER SETUP FOR ATTACHMENTS ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- DATABASE CONNECTION HELPER ---
def get_db_connection():
    try:
        from database import get_connection as conn
        return conn()
    except ImportError:
        try:
            from db import get_connection as conn
            return conn()
        except ImportError:
            try:
                return mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="3251",
                    database="campusconnect",
                )
            except Exception as e:
                st.error(f"⚠️ Database Connection Error: {e}")
                return None

# --- INITIALIZE ALL TABLES ---
def init_all_tables():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # 1. Notices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty_notices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                file_path VARCHAR(512),
                posted_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 2. Notes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject VARCHAR(150) NOT NULL,
                title VARCHAR(255) NOT NULL,
                file_path VARCHAR(512) NOT NULL,
                uploaded_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 3. Assignments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty_assignments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                deadline DATE NOT NULL,
                description TEXT NOT NULL,
                file_path VARCHAR(512),
                posted_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 4. Doubts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_doubts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(150) NOT NULL,
                question TEXT NOT NULL,
                reply TEXT,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Error initializing database tables: {e}")
    finally:
        conn.close()


# =========================================================
# 1. NOTICES PAGE LOGIC
# =========================================================
def render_notices_page():
    st.title("📢 Campus Notices & Announcements")
    st.caption("Post official announcements, upload attachments, and manage previous notices.")
    st.markdown("---")

    tab_post, tab_manage = st.tabs(["➕ Post New Announcement", "📋 Manage & View All Notices"])

    with tab_post:
        st.subheader("🚀 Publish New Notice")
        
        with st.form("notice_form", clear_on_submit=True):
            notice_title = st.text_input("Notice Title", placeholder="e.g. Mid-Semester Exam Schedule")
            notice_desc = st.text_area("Announcement Details", placeholder="Write full description here...")
            
            uploaded_file = st.file_uploader(
                "Attach Document / Image (PDF, PNG, JPG, TXT, XLSX, DOCX)",
                type=["pdf", "png", "jpg", "jpeg", "txt", "xlsx", "xls", "doc", "docx"]
            )
            
            submit_notice = st.form_submit_button("Publish Announcement", type="primary", use_container_width=True)

        if submit_notice:
            if not notice_title.strip() or not notice_desc.strip():
                st.warning("⚠️ Please fill in both the title and announcement details!")
            else:
                try:
                    final_file_path = None
                    if uploaded_file is not None:
                        safe_filename = f"notice_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name.replace(' ', '_')}"
                        file_path = os.path.join(UPLOAD_DIR, safe_filename)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        final_file_path = file_path

                    posted_by = st.session_state.get("name", st.session_state.get("username", "Sir"))

                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO faculty_notices (title, description, file_path, posted_by) VALUES (%s, %s, %s, %s)",
                            (notice_title.strip(), notice_desc.strip(), final_file_path, posted_by),
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success("✅ Notice successfully uploaded and published!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error publishing announcement: {e}")

    with tab_manage:
        st.subheader("📋 Active Notices & Announcements")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM faculty_notices ORDER BY created_at DESC")
                notices_list = cursor.fetchall()
                cursor.close()
                conn.close()

                if not notices_list:
                    st.info("ℹ️ No announcements posted yet.")
                else:
                    for notice in notices_list:
                        with st.container(border=True):
                            st.subheader(f"📌 {notice['title']}")
                            st.caption(f"📅 Posted on: {notice['created_at']} | By: **{notice.get('posted_by', 'Sir')}**")
                            st.write(notice["description"])

                            f_path = notice.get("file_path")
                            if f_path and os.path.exists(f_path):
                                original_filename = os.path.basename(f_path).split('_', 2)[-1]
                                file_ext = os.path.splitext(f_path)[1].lower()

                                if file_ext in [".png", ".jpg", ".jpeg"]:
                                    st.image(f_path, caption=f"Attachment: {original_filename}", use_container_width=True)

                                with open(f_path, "rb") as f_obj:
                                    st.download_button(
                                        label=f"📥 Download Attachment ({original_filename})",
                                        data=f_obj,
                                        file_name=original_filename,
                                        key=f"dl_notice_{notice['id']}",
                                    )
                            elif f_path:
                                st.warning("⚠️ Attachment file missing from server storage.")

                            if st.button("🗑️ Delete Notice", key=f"del_notice_{notice['id']}"):
                                conn_del = get_db_connection()
                                if conn_del:
                                    cur_del = conn_del.cursor()
                                    cur_del.execute("DELETE FROM faculty_notices WHERE id = %s", (notice["id"],))
                                    conn_del.commit()
                                    cur_del.close()
                                    conn_del.close()
                                    st.success("Notice deleted successfully!")
                                    st.rerun()
        except Exception as e:
            st.error(f"Error loading announcements: {e}")


# =========================================================
# 2. NOTES & MATERIALS PAGE LOGIC
# =========================================================
def render_notes_page():
    st.title("📚 Upload & Manage Study Materials")
    st.caption("Upload lecture slides, notes, or reference documents for students.")
    st.markdown("---")

    tab_upload, tab_view = st.tabs(["➕ Upload New Note", "📖 Manage Existing Notes"])

    with tab_upload:
        st.subheader("📄 Publish Study Material")
        
        with st.form("notes_form", clear_on_submit=True):
            subject = st.selectbox("Subject", ["Artificial Intelligence", "Machine Learning", "Data Structures", "Engineering Math", "Computer Networks"])
            note_title = st.text_input("Topic / Lecture Title", placeholder="e.g. Module 1 Complete Notes")
            uploaded_note = st.file_uploader("Upload Document (PDF, PPT, DOCX, TXT)", type=["pdf", "ppt", "pptx", "docx", "txt"])

            submit_note = st.form_submit_button("Upload Material", type="primary", use_container_width=True)

        if submit_note:
            if not note_title.strip() or not uploaded_note:
                st.warning("⚠️ Please provide a topic title and attach a document file.")
            else:
                try:
                    safe_filename = f"note_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_note.name.replace(' ', '_')}"
                    file_path = os.path.join(UPLOAD_DIR, safe_filename)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_note.getbuffer())

                    uploaded_by = st.session_state.get("name", st.session_state.get("username", "Sir"))

                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO faculty_notes (subject, title, file_path, uploaded_by) VALUES (%s, %s, %s, %s)",
                            (subject, note_title.strip(), file_path, uploaded_by)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success("✅ Study material successfully uploaded!")
                except Exception as e:
                    st.error(f"Error uploading note: {e}")

    with tab_view:
        st.subheader("📁 Uploaded Materials History")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM faculty_notes ORDER BY created_at DESC")
                notes_list = cursor.fetchall()
                cursor.close()
                conn.close()

                if not notes_list:
                    st.info("No study materials uploaded yet.")
                else:
                    for note in notes_list:
                        with st.container(border=True):
                            st.subheader(f"📖 [{note['subject']}] {note['title']}")
                            st.caption(f"📅 Uploaded on: {note['created_at']} | By: **{note.get('uploaded_by', 'Sir')}**")

                            f_path = note.get("file_path")
                            if f_path and os.path.exists(f_path):
                                original_filename = os.path.basename(f_path).split('_', 2)[-1]
                                with open(f_path, "rb") as f_obj:
                                    st.download_button(
                                        label=f"📥 Download Material ({original_filename})",
                                        data=f_obj,
                                        file_name=original_filename,
                                        key=f"dl_note_{note['id']}"
                                    )
                            else:
                                st.warning("⚠️ File missing from server.")

                            if st.button("🗑️ Delete Material", key=f"del_note_{note['id']}"):
                                conn_del = get_db_connection()
                                if conn_del:
                                    cur_del = conn_del.cursor()
                                    cur_del.execute("DELETE FROM faculty_notes WHERE id = %s", (note["id"],))
                                    conn_del.commit()
                                    cur_del.close()
                                    conn_del.close()
                                    st.success("Material deleted successfully!")
                                    st.rerun()
        except Exception as e:
            st.error(f"Error fetching notes: {e}")


# =========================================================
# 3. ASSIGNMENTS & QUIZZES PAGE LOGIC
# =========================================================
def render_assignments_page():
    st.title("📝 Assignments & Quizzes Manager")
    st.caption("Post assignments with document attachments and view student management logs.")
    st.markdown("---")

    tab1, tab2 = st.tabs(["➕ Post New Assignment", "📋 Manage & View Assignments"])

    with tab1:
        st.subheader("🚀 Create Assignment")
        
        with st.form("assignment_form", clear_on_submit=True):
            assign_title = st.text_input("Assignment Title", placeholder="e.g. Assignment 1: Machine Learning Regression")
            deadline = st.date_input("Submission Deadline")
            description = st.text_area("Instructions / Guidelines", placeholder="Write instructions for students...")
            
            assign_file = st.file_uploader(
                "Attach Assignment Question Paper / PDF (Optional)",
                type=["pdf", "doc", "docx", "txt", "zip"]
            )

            submit_assignment = st.form_submit_button("Post Assignment", type="primary", use_container_width=True)

        if submit_assignment:
            if not assign_title.strip() or not description.strip():
                st.warning("⚠️ Please provide an assignment title and instructions.")
            else:
                try:
                    final_file_path = None
                    if assign_file is not None:
                        safe_filename = f"assign_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{assign_file.name.replace(' ', '_')}"
                        file_path = os.path.join(UPLOAD_DIR, safe_filename)
                        with open(file_path, "wb") as f:
                            f.write(assign_file.getbuffer())
                        final_file_path = file_path

                    posted_by = st.session_state.get("name", st.session_state.get("username", "Sir"))

                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO faculty_assignments (title, deadline, description, file_path, posted_by) VALUES (%s, %s, %s, %s, %s)",
                            (assign_title.strip(), deadline, description.strip(), final_file_path, posted_by)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success("✅ Assignment successfully posted!")
                except Exception as e:
                    st.error(f"Error posting assignment: {e}")

    with tab2:
        st.subheader("📋 Active Assignments List")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM faculty_assignments ORDER BY created_at DESC")
                assignments_list = cursor.fetchall()
                cursor.close()
                conn.close()

                if not assignments_list:
                    st.info("No assignments posted yet.")
                else:
                    for asn in assignments_list:
                        with st.container(border=True):
                            st.subheader(f"📌 {asn['title']}")
                            st.caption(f"⏰ Deadline: **{asn['deadline']}** | Posted by: **{asn.get('posted_by', 'Sir')}**")
                            st.write(asn["description"])

                            f_path = asn.get("file_path")
                            if f_path and os.path.exists(f_path):
                                original_filename = os.path.basename(f_path).split('_', 2)[-1]
                                with open(f_path, "rb") as f_obj:
                                    st.download_button(
                                        label=f"📥 Download Question Paper ({original_filename})",
                                        data=f_obj,
                                        file_name=original_filename,
                                        key=f"dl_assign_{asn['id']}"
                                    )

                            if st.button("🗑️ Delete Assignment", key=f"del_assign_{asn['id']}"):
                                conn_del = get_db_connection()
                                if conn_del:
                                    cur_del = conn_del.cursor()
                                    cur_del.execute("DELETE FROM faculty_assignments WHERE id = %s", (asn["id"],))
                                    conn_del.commit()
                                    cur_del.close()
                                    conn_del.close()
                                    st.success("Assignment deleted successfully!")
                                    st.rerun()
        except Exception as e:
            st.error(f"Error loading assignments: {e}")


# =========================================================
# 4. STUDENT DOUBT FORUM PAGE LOGIC
# =========================================================
def render_doubts_page():
    st.title("❓ Student Doubt Forum")
    st.caption("Review actual student queries, clear doubts, and manage solutions.")
    st.markdown("---")

    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student_doubts ORDER BY created_at DESC")
            doubts_list = cursor.fetchall()
            cursor.close()
            conn.close()

            if not doubts_list:
                st.info("ℹ️ No real student doubts raised yet.")
            else:
                for doubt in doubts_list:
                    status_emoji = "🟢" if doubt['status'] == "Resolved" else "🟠"
                    with st.expander(f"{status_emoji} Q: {doubt['question']} — [Asked by: {doubt['student_name']}]"):
                        st.write(f"**Question:** {doubt['question']}")
                        st.caption(f"Raised on: {doubt['created_at']} | Status: **{doubt['status']}**")

                        if doubt['reply']:
                            st.success(f"**Faculty Reply:** {doubt['reply']}")
                        else:
                            with st.form(key=f"reply_form_{doubt['id']}"):
                                fac_reply = st.text_area("Type your solution / reply here...", key=f"reply_txt_{doubt['id']}")
                                send_btn = st.form_submit_button("Send Reply & Resolve")

                                if send_btn:
                                    if not fac_reply.strip():
                                        st.warning("Reply cannot be empty!")
                                    else:
                                        conn_up = get_db_connection()
                                        if conn_up:
                                            cur_up = conn_up.cursor()
                                            cur_up.execute(
                                                "UPDATE student_doubts SET reply = %s, status = 'Resolved' WHERE id = %s",
                                                (fac_reply.strip(), doubt['id'])
                                            )
                                            conn_up.commit()
                                            cur_up.close()
                                            conn_up.close()
                                            st.success("✅ Reply submitted successfully!")
                                            st.rerun()
    except Exception as e:
        st.error(f"Error fetching real student doubts: {e}")


# =========================================================
# MAIN ENTRYPOINT FUNCTION CALLED BY APP.PY
# =========================================================
def show_faculty_dashboard():
    init_all_tables()

    if "faculty_active_page" not in st.session_state:
        st.session_state["faculty_active_page"] = "Dashboard"

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title("👨‍🏫 Faculty Portal")
    st.sidebar.markdown(f"**Welcome, Sir!**")
    st.sidebar.markdown("---")

    if st.sidebar.button("📊 Dashboard Home", use_container_width=True):
        st.session_state["faculty_active_page"] = "Dashboard"
    if st.sidebar.button("📢 Notice Board", use_container_width=True):
        st.session_state["faculty_active_page"] = "Notices"
    if st.sidebar.button("📚 Notes & Materials", use_container_width=True):
        st.session_state["faculty_active_page"] = "Notes"
    if st.sidebar.button("📝 Assignments & Quizzes", use_container_width=True):
        st.session_state["faculty_active_page"] = "Assignments"
    if st.sidebar.button("❓ Doubt Forum", use_container_width=True):
        st.session_state["faculty_active_page"] = "Doubts"

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # --- MAIN CONTENT ROUTING ---
    page = st.session_state["faculty_active_page"]

    if page == "Dashboard":
        st.title("📊 Welcome Back, Sir!")
        st.markdown("Here is your central control hub for managing coursework, student interactions, and official announcements.")
        
        active_notices_count = 0
        pending_doubts_count = 0
        resolved_doubts_count = 0
        active_assignments_count = 0

        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM faculty_notices")
                res = cursor.fetchone()
                if res:
                    active_notices_count = res[0]

                cursor.execute("SELECT COUNT(*) FROM student_doubts WHERE status = 'Pending'")
                res_p = cursor.fetchone()
                if res_p:
                    pending_doubts_count = res_p[0]

                cursor.execute("SELECT COUNT(*) FROM student_doubts WHERE status = 'Resolved'")
                res_r = cursor.fetchone()
                if res_r:
                    resolved_doubts_count = res_r[0]

                cursor.execute("SELECT COUNT(*) FROM faculty_assignments")
                res_a = cursor.fetchone()
                if res_a:
                    active_assignments_count = res_a[0]

                cursor.close()
                conn.close()
        except Exception:
            pass

        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🟠 Active / Recent Doubts", value=pending_doubts_count)
        with col2:
            st.metric(label="🟢 Solved Doubts", value=resolved_doubts_count)
        with col3:
            st.metric(label="📢 Active Notices", value=active_notices_count)

        col4, col5, _ = st.columns(3)
        with col4:
            st.metric(label="📝 Active Assignments", value=active_assignments_count)
        with col5:
            st.metric(label="📌 Total Posts/Notices", value=active_notices_count)
            
        st.markdown("### 🚀 Quick Navigation Guide")
        st.info("Use the left sidebar buttons to navigate to Notices, upload study materials, post assignments with attachments, or resolve actual student doubts.")

    elif page == "Notices":
        render_notices_page()

    elif page == "Notes":
        render_notes_page()

    elif page == "Assignments":
        render_assignments_page()

    elif page == "Doubts":
        render_doubts_page()