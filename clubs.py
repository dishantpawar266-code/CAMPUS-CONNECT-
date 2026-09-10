import os
import mysql.connector
import streamlit as st

# --- DIRECTORY CONFIGURATION FOR UPLOADS ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# --- MYSQL DATABASE CONNECTION HELPER ---
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


# --- DATABASE SETUP & DUMMY SEEDING ---
def init_clubs_db():
    conn = get_db_connection() 
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # 1. Create Clubs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clubs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                lead_name VARCHAR(100) NOT NULL,
                description TEXT
            )
        """)

        # 2. Create Club Posts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS club_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                club_id INT NOT NULL,
                message TEXT NOT NULL,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
            )
        """)

        # 3. Create Club Messages Table (With reply column)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS club_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                club_id INT NOT NULL,
                sender_name VARCHAR(100) NOT NULL,
                sender_email VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                reply TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
            )
        """)

        # Seed initial clubs if empty
        cursor.execute("SELECT COUNT(*) FROM clubs")
        if cursor.fetchone()[0] == 0:
            sample_clubs = [
                (
                    "Coding Club (DevsUnit)",
                    "Technology",
                    "Aman Verma",
                    "Official coding & open-source community for hackathons and projects.",
                ),
                (
                    "Robotics & Automation",
                    "Technical",
                    "Priya Sharma",
                    "Building autonomous robots, IoT hardware, and drone tech.",
                ),
                (
                    "Cultural & Drama Society",
                    "Arts",
                    "Rohan Mehta",
                    "Annual fest organizing, music, drama, and stage performances.",
                ),
            ]
            cursor.executemany(
                "INSERT INTO clubs (name, category, lead_name, description) VALUES (%s, %s, %s, %s)",
                sample_clubs,
            )

        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Error initializing Clubs Database: {e}")
    finally:
        conn.close()


# =========================================================
# 1. STUDENT VIEW: PUBLIC CLUB FEED & MESSAGE FORM
# =========================================================
def show_student_club_view(club):
    if st.button("← Back to All Clubs"):
        st.session_state.active_club_id = None
        st.rerun()

    st.markdown("---")
    st.title(f"🛡️ {club['name']}")
    st.caption(f"Category: **{club['category']}** | Club Leader: **{club['lead_name']}**")
    st.info(f"**About:** {club['description']}")

    st.markdown("---")
    tab_feed, tab_contact = st.tabs(["📢 Official Announcements & Photos", "📩 Contact Club Leader"])

    # --- TAB 1: READ-ONLY OFFICIAL FEED ---
    with tab_feed:
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM club_posts WHERE club_id = %s ORDER BY created_at DESC",
                    (club["id"],),
                )
                posts = cursor.fetchall()
                conn.close()

                if not posts:
                    st.info("Abhi tak club leader ne koi update post nahi kiya hai.")
                else:
                    for post in posts:
                        with st.container(border=True):
                            st.caption(f"📅 Posted on: {post['created_at']}")
                            st.write(post["message"])
                            if post.get("image_url"):
                                img_path = post["image_url"]
                                if not img_path.startswith("http"):
                                    img_path = os.path.join(UPLOAD_DIR, os.path.basename(img_path))
                                if os.path.exists(img_path) or img_path.startswith("http"):
                                    st.image(img_path, use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching posts: {e}")

    # --- TAB 2: SEND MESSAGE TO LEADER & VIEW REPLIES ---
    with tab_contact:
        st.subheader(f"💬 Send a Private Message to {club['name']} Leader")
        student_name = st.session_state.get("name", st.session_state.get("username", "Student"))
        student_email = st.session_state.get("user_data", {}).get("email") or st.session_state.get("email", "student@campus.com")

        with st.form(key=f"msg_form_{club['id']}", clear_on_submit=True):
            msg_text = st.text_area(
                "Your Query / Message",
                placeholder="Ask questions about recruitment, upcoming events, or joining procedure...",
            )
            submit_msg = st.form_submit_button("📤 Send Message to Leader", type="primary", use_container_width=True)

            if submit_msg:
                if not msg_text.strip():
                    st.warning("Please write a message before sending!")
                else:
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO club_messages (club_id, sender_name, sender_email, message) VALUES (%s, %s, %s, %s)",
                                (club["id"], student_name, student_email, msg_text.strip()),
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Your message has been sent directly to {club['lead_name']}!")
                    except Exception as e:
                        st.error(f"Error sending message: {e}")

        st.markdown("---")
        st.subheader("📬 Your Sent Queries & Leader Replies")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM club_messages WHERE club_id = %s AND sender_email = %s ORDER BY created_at DESC",
                    (club["id"], student_email),
                )
                my_messages = cursor.fetchall()
                conn.close()

                if not my_messages:
                    st.info("You haven't sent any messages to this club yet.")
                else:
                    for m in my_messages:
                        with st.container(border=True):
                            st.caption(f"Sent on: {m['created_at']}")
                            st.write(f"**You:** {m['message']}")
                            if m.get("reply"):
                                st.success(f"👑 **Leader Reply:** {m['reply']}")
                            else:
                                st.info("⏳ Waiting for leader response...")
        except Exception as e:
            st.error(f"Error fetching your messages: {e}")


# =========================================================
# 2. CLUB LEADER DASHBOARD
# =========================================================
def show_leader_dashboard(club):
    col_head, col_out = st.columns([4, 1])
    with col_head:
        st.title(f"👑 Leader Portal: {club['name']}")
        st.caption(f"Logged in as Club Leader: **{club['lead_name']}**")
    with col_out:
        st.write(" ")
        if st.button("🚪 Leader Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.name = ""
            st.session_state.user_data = {}
            st.rerun()

    st.markdown("---")
    tab_post, tab_inbox = st.tabs(["➕ Post & Manage Announcements", "📥 Student Messages / Queries"])

    # --- TAB 1: CREATE & DELETE OFFICIAL POSTS (WITHOUT FORM TO SUPPORT FILE UPLOADER) ---
    with tab_post:
        st.subheader("📢 Share Updates or Photos with Campus")
        
        post_msg = st.text_area(
            "Announcement Details",
            placeholder="Write official announcement, event schedule, or news...",
            key="leader_post_msg"
        )
        uploaded_file = st.file_uploader("Upload Photo (Optional)", type=["png", "jpg", "jpeg"], key="leader_post_file")
        img_url = st.text_input("Or Image URL (Optional)", placeholder="https://example.com/poster.jpg", key="leader_post_url")
        
        if st.button("🚀 Publish Announcement", type="primary", use_container_width=True):
            if not post_msg.strip():
                st.warning("Announcement text cannot be empty!")
            else:
                try:
                    final_image_path = None
                    if uploaded_file is not None:
                        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        final_image_path = file_path
                    elif img_url.strip():
                        final_image_path = img_url.strip()

                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO club_posts (club_id, message, image_url) VALUES (%s, %s, %s)",
                            (club["id"], post_msg.strip(), final_image_path),
                        )
                        conn.commit()
                        conn.close()
                        st.success("Official update published to club feed!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error publishing post: {e}")

        st.markdown("---")
        st.subheader("🗑️ Existing Announcements (Manage / Delete)")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM club_posts WHERE club_id = %s ORDER BY created_at DESC",
                    (club["id"],),
                )
                posts = cursor.fetchall()
                conn.close()

                if not posts:
                    st.info("No active announcements found.")
                else:
                    for post in posts:
                        with st.container(border=True):
                            st.caption(f"📅 Posted on: {post['created_at']}")
                            st.write(post["message"])
                            if post.get("image_url"):
                                img_path = post["image_url"]
                                if not img_path.startswith("http") and os.path.exists(img_path):
                                    st.image(img_path, use_container_width=True)
                                elif img_path.startswith("http"):
                                    st.image(img_path, use_container_width=True)

                            if st.button("🗑️ Delete Announcement", key=f"del_post_{post['id']}"):
                                try:
                                    conn_del = get_db_connection()
                                    if conn_del:
                                        cur_del = conn_del.cursor()
                                        cur_del.execute("DELETE FROM club_posts WHERE id = %s", (post["id"],))
                                        conn_del.commit()
                                        conn_del.close()
                                        st.success("Announcement deleted successfully!")
                                        st.rerun()
                                except Exception as err:
                                    st.error(f"Error deleting post: {err}")
        except Exception as e:
            st.error(f"Error loading posts for deletion: {e}")

    # --- TAB 2: VIEW RECEIVED STUDENT MESSAGES & REPLY ---
    with tab_inbox:
        st.subheader("📬 Messages Received from Students")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM club_messages WHERE club_id = %s ORDER BY created_at DESC",
                    (club["id"],),
                )
                messages = cursor.fetchall()
                conn.close()

                if not messages:
                    st.info("No student messages received yet.")
                else:
                    for msg in messages:
                        with st.container(border=True):
                            st.markdown(f"👤 **{msg['sender_name']}** (`{msg['sender_email']}`)")
                            st.caption(f"Received at: {msg['created_at']}")
                            st.write(msg["message"])

                            if msg.get("reply"):
                                st.info(f"💬 **Your Reply:** {msg['reply']}")
                            else:
                                with st.form(key=f"reply_form_{msg['id']}"):
                                    reply_text = st.text_area(
                                        "Reply to Student",
                                        placeholder="Type your response here...",
                                    )
                                    send_reply = st.form_submit_button("📩 Send Reply")
                                    if send_reply:
                                        if not reply_text.strip():
                                            st.warning("Reply cannot be empty!")
                                        else:
                                            try:
                                                conn_rep = get_db_connection()
                                                if conn_rep:
                                                    cur_rep = conn_rep.cursor()
                                                    cur_rep.execute(
                                                        "UPDATE club_messages SET reply = %s WHERE id = %s",
                                                        (reply_text.strip(), msg["id"]),
                                                    )
                                                    conn_rep.commit()
                                                    conn_rep.close()
                                                    st.success("Reply sent successfully!")
                                                    st.rerun()
                                            except Exception as rep_err:
                                                st.error(f"Error sending reply: {rep_err}")
        except Exception as e:
            st.error(f"Error loading messages: {e}")


# =========================================================
# 3. MAIN CLUBS DIRECTORY (FOR STUDENTS)
# =========================================================
def show_clubs_page():
    init_clubs_db()

    if "active_club_id" not in st.session_state:
        st.session_state.active_club_id = None

    if st.session_state.active_club_id:
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM clubs WHERE id = %s", (st.session_state.active_club_id,))
                selected_club = cursor.fetchone()
                conn.close()

                if selected_club:
                    show_student_club_view(selected_club)
                    return
        except Exception as e:
            st.error(f"Database error: {e}")

    st.title("🎪 Campus Clubs & Communities")
    st.caption("Explore student clubs, read official announcements, and contact leaders.")
    st.markdown("---")

    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clubs ORDER BY id DESC")
            clubs_list = cursor.fetchall()
            conn.close()

            if not clubs_list:
                st.info("Filhaal koi club registered nahi hai.")
            else:
                col1, col2 = st.columns(2)
                for idx, club in enumerate(clubs_list):
                    target_col = col1 if idx % 2 == 0 else col2
                    with target_col:
                        with st.container(border=True):
                            st.subheader(f"🛡️ {club['name']}")
                            st.caption(f"Category: **{club['category']}** | Leader: **{club['lead_name']}**")
                            st.write(club["description"])

                            if st.button(
                                "View Updates & Contact →",
                                key=f"view_{club['id']}",
                                type="primary",
                                use_container_width=True,
                            ):
                                st.session_state.active_club_id = club["id"]
                                st.rerun()
    except Exception as e:
        st.error(f"Database error: {e}")