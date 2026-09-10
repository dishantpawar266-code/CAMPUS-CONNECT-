import datetime
import os
import mysql.connector
import streamlit as st

# --- ATTACHMENTS FOLDER ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


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


# =====================================================
# MODULE IMPORTS (SAFE FALLBACKS)
# =====================================================
try:
    from notes import show_notes_page
except Exception as e:
    def show_notes_page():
        st.error(f"❌ Error loading notes.py module: {e}")


try:
    from tasks import fetch_tasks, show_task_planner_page
except Exception:
    def show_task_planner_page():
        st.title("📅 Task Planner")
        st.info("Task planner module ready.")
    def fetch_tasks(email):
        return []


try:
    from assignments import show_assignments_page
except Exception:
    def show_assignments_page():
        st.title("📝 Assignments & Submissions")


try:
    from doubts import show_doubt_forum_page
except Exception:
    def show_doubt_forum_page():
        st.title("💬 Student Doubt Forum")


try:
    from clubs import show_clubs_page
except Exception:
    def show_clubs_page():
        st.title("🎪 Clubs & Communities")


try:
    from ai_assistant import show_ai_assistant_page
except Exception:
    def show_ai_assistant_page():
        st.title("🤖 AI Assistant")


# =====================================================
# STUDENT NOTICES PAGE (VIEW & DOWNLOAD ONLY)
# =====================================================
def show_student_notices_page():
    st.title("📢 Campus Notices & Announcements")
    st.caption("View official announcements and download reference materials posted by faculty.")
    st.markdown("---")

    try:
        conn = get_connection()
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
                        st.caption(f"📅 Posted on: {notice['created_at']} | By: **{notice.get('posted_by', 'Faculty')}**")
                        st.write(notice["description"])

                        f_path = notice.get("file_path")
                        if f_path and os.path.exists(f_path):
                            original_filename = os.path.basename(f_path).split('_', 2)[-1]
                            file_ext = os.path.splitext(f_path)[1].lower()

                            if file_ext in [".png", ".jpg", ".jpeg"]:
                                st.image(f_path, caption=f"Attachment Preview: {original_filename}", use_container_width=True)

                            with open(f_path, "rb") as f_obj:
                                st.download_button(
                                    label=f"📥 Download Attachment ({original_filename})",
                                    data=f_obj,
                                    file_name=original_filename,
                                    key=f"student_dl_notice_{notice['id']}",
                                )
                        elif f_path:
                            st.warning("⚠️ Attachment file missing from server storage.")
    except Exception as e:
        st.error(f"Error loading announcements: {e}")


# =====================================================
# STUDENT DOUBT FORUM PAGE (UNDER MAINTENANCE)
# =====================================================
def show_student_doubt_forum_page():
    st.title("💬 Student Doubt Forum")
    st.caption("Ask questions, clear your academic doubts, and track faculty responses.")
    st.markdown("---")

    student_name = st.session_state.get("name", st.session_state.get("username", "DISHANT H PAWAR"))
    
    st.warning("⚠️ **Module Under Maintenance**")
    st.info("We are currently updating the requirements, database structure, and teacher response workflow for this section. Please check back shortly!")


# =====================================================
# NAVIGATION HELPER
# =====================================================
def set_page(page_name):
    st.session_state["active_page"] = page_name


# Helper to get live counts from DB for Metrics (Synced with Faculty Tables)
def fetch_dashboard_counts(student_name=""):
    counts = {"notices": 0, "assignments": 0, "notes": 0, "doubts": 0}
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # 1. Faculty Notices Count
            try:
                cursor.execute("SELECT COUNT(*) FROM faculty_notices")
                res = cursor.fetchone()
                if res:
                    counts["notices"] = res[0]
            except Exception:
                pass

            # 2. Faculty Assignments Count
            try:
                cursor.execute("SELECT COUNT(*) FROM faculty_assignments")
                res = cursor.fetchone()
                if res:
                    counts["assignments"] = res[0]
            except Exception:
                pass

            # 3. Faculty Notes Count
            try:
                cursor.execute("SELECT COUNT(*) FROM faculty_notes")
                res = cursor.fetchone()
                if res:
                    counts["notes"] = res[0]
            except Exception:
                pass

            # 4. Resolved Doubts Count
            try:
                if student_name:
                    cursor.execute(
                        "SELECT COUNT(*) FROM student_doubts WHERE student_name = %s AND status = 'Resolved'",
                        (student_name,),
                    )
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM student_doubts WHERE status = 'Resolved'"
                    )
                res = cursor.fetchone()
                if res:
                    counts["doubts"] = res[0]
            except Exception:
                pass

            cursor.close()
        except Exception:
            pass
        finally:
            conn.close()
    return counts


# =====================================================
# MAIN STUDENT DASHBOARD ENTRYPOINT FUNCTION
# =====================================================
def show_student_dashboard():
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"

    user_email = st.session_state.get("user_data", {}).get("email") or st.session_state.get("email", "")
    
    student_name = st.session_state.get(
        "name", st.session_state.get("username", "DISHANT H PAWAR")
    )

    # ---------------- SIDEBAR NAVIGATION ---------------- #
    with st.sidebar:
        st.markdown("## 🎓 CampusConnect")
        st.write(f"👤 **{student_name}**")
        st.caption("Role: Student")
        st.markdown("---")

        st.button(
            "🏠 Dashboard",
            on_click=set_page,
            args=("Dashboard",),
            use_container_width=True,
        )
        st.button(
            "📅 Task Planner",
            on_click=set_page,
            args=("Task Planner",),
            use_container_width=True,
        )
        st.button(
            "📚 My Notes",
            on_click=set_page,
            args=("My Notes",),
            use_container_width=True,
        )
        st.button(
            "💬 Doubt Forum",
            on_click=set_page,
            args=("Doubt Forum",),
            use_container_width=True,
        )
        st.button(
            "🎪 Clubs & Communities",
            on_click=set_page,
            args=("Clubs",),
            use_container_width=True,
        )
        st.button(
            "📝 Assignments",
            on_click=set_page,
            args=("Assignments",),
            use_container_width=True,
        )
        st.button(
            "📢 Notices",
            on_click=set_page,
            args=("Notices",),
            use_container_width=True,
        )
        st.button(
            "🤖 AI Assistant",
            on_click=set_page,
            args=("AI Assistant",),
            use_container_width=True,
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state["active_page"] = "Dashboard"
            st.rerun()

    # ---------------- PAGE ROUTING ---------------- #
    page = st.session_state["active_page"]

    if page == "Task Planner":
        show_task_planner_page()
        return

    if page == "My Notes":
        show_notes_page()
        return

    if page == "Doubt Forum":
        show_student_doubt_forum_page()
        return

    if page == "Clubs":
        show_clubs_page()
        return

    if page == "Assignments":
        show_assignments_page()
        return

    if page == "Notices":
        show_student_notices_page()
        return

    if page == "AI Assistant":
        show_ai_assistant_page()
        return

    # ---------------- MAIN DASHBOARD HOME VIEW ---------------- #
    st.title(f"👋 Welcome back, {student_name}!")
    st.caption("🎓 B.Tech AI & ML | Semester 4")
    st.markdown("---")

    # Fetch live counts from DB
    db_counts = fetch_dashboard_counts(student_name)

    # Live Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("New Notices", db_counts["notices"])
    with c2:
        st.metric("Active Assignments", db_counts["assignments"])
    with c3:
        st.metric("Shared Notes", db_counts["notes"])
    with c4:
        st.metric("Solved Doubts", db_counts["doubts"])

    st.markdown("---")

    # --- DOUBT HISTORY & NOTICES SECTION ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("💬 My Doubt History")
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT question, reply, status FROM student_doubts WHERE student_name = %s ORDER BY created_at DESC", 
                    (student_name,)
                )
                my_doubts = cursor.fetchall()
                cursor.close()
                conn.close()
                
                if not my_doubts:
                    st.info("No doubts asked yet.")
                else:
                    for d in my_doubts:
                        status_color = "🟢" if d['status'] == 'Resolved' else "🟠"
                        with st.expander(f"{status_color} {d['question'][:30]}..."):
                            st.write(f"**Q:** {d['question']}")
                            if d['reply']:
                                st.success(f"**Faculty Answer:** {d['reply']}")
                            else:
                                st.warning("Status: Pending (Waiting for Faculty)")
            except Exception:
                st.info("Doubt history table not found or empty.")

    with col_right:
        st.subheader("📢 Recent Notices")
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT title, description FROM faculty_notices ORDER BY created_at DESC LIMIT 5")
                recent_notices = cursor.fetchall()
                cursor.close()
                conn.close()
                
                if not recent_notices:
                    st.info("No notices available.")
                else:
                    for n in recent_notices:
                        with st.container(border=True):
                            st.markdown(f"**{n['title']}**")
                            st.caption(n['description'][:50] + "...")
            except Exception:
                st.info("Notices table not found or empty.")

    st.markdown("---")

    # Tasks Overview Card
    tasks = fetch_tasks(user_email) if user_email else []
    completed = sum(1 for t in tasks if t.get("is_completed"))
    total = len(tasks)

    with st.container(border=True):
        col_title, col_btn = st.columns([3, 1])
        with col_title:
            st.subheader("📅 Today's Task Planner")
            st.caption(f"Progress: **{completed}/{total} Tasks Completed**")

        with col_btn:
            st.write(" ")
            st.button(
                "Manage Tasks →",
                key="dash_open_planner",
                on_click=set_page,
                args=("Task Planner",),
                use_container_width=True,
            )

        if not tasks:
            st.write("No tasks planned yet.")
        else:
            for t in tasks[:3]:
                status_icon = "✅" if t.get("is_completed") else "⏳"
                st.write(
                    f"{status_icon} **[{t.get('time_slot')}]** {t.get('title')}"
                ) 
               