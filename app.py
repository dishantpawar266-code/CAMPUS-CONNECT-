import base64
import os
import auth
import mysql.connector
import streamlit as st
from clubs import show_leader_dashboard
from faculty_dashboard import show_faculty_dashboard
from student_dashboard import show_student_dashboard

# =========================================================
# PAGE CONFIG & SESSION STATE INITIALIZATION
# =========================================================

st.set_page_config(
    page_title="RCPIT Campus Connect", page_icon="🎓", layout="wide"
)


def initialize_session_state():
    defaults = {
        "logged_in": False,
        "role": None,
        "name": "",
        "auth_mode": "login",
        "user_data": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


initialize_session_state()


# --- DB CONNECTION FOR CLUB LEADER & FACULTY ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="3251", database="campusconnect"
    )


# --- HELPER FOR EMBEDDING LOGO/IMAGE IN HTML ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# =========================================================
# STYLING & SHARP VISIBLE BORDER UI INTEGRATION
# =========================================================

college_image_path = "background_image.jpg"
bg_base64 = get_image_base64(college_image_path)

if bg_base64:
    app_bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(11, 19, 36, 0.88), rgba(11, 19, 36, 0.93)), 
                    url("data:image/jpeg;base64,{bg_base64}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #F1F5F9 !important;
    }}
    """
else:
    app_bg_style = """
    .stApp {
        background-color: #0F172A !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #F1F5F9 !important;
    }
    """

st.markdown(
    f"""
    <style>
    {app_bg_style}

    /* 1. Reset layout wrappers */
    [data-testid="stVerticalBlock"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"], 
    [data-testid="stHorizontalBlock"], 
    .element-container {{
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    /* 2. Sharp, Clearly Visible Solid Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: #1E293B !important;
        border-radius: 12px !important;
        padding: 24px !important;
        border: 1.5px solid #475569 !important;
        border-top: 4px solid #3B82F6 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
        opacity: 1 !important;
    }}

    /* 3. Headers & Labels */
    h1, h2, h3, h4, label, p {{
        color: #F8FAFC !important;
    }}

    /* 4. Professional Action Buttons with Clear Borders */
    .stButton button {{
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: 1.5px solid #60A5FA !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton button:hover {{
        background-color: #1D4ED8 !important;
        border-color: #93C5FD !important;
        box-shadow: 0 5px 14px rgba(37, 99, 235, 0.45) !important;
    }}

    /* 5. Clearly Visible Form Input Fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {{
        background-color: #0F172A !important;
        border: 1.5px solid #64748B !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        padding: 10px 14px !important;
        opacity: 1 !important;
    }}
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
        border: 1.5px solid #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
    }}

    /* 6. Distinct Enterprise Header Banner */
    .enterprise-header {{
        background: #1E293B !important;
        padding: 24px 32px;
        border-radius: 12px;
        color: #F9FAFB !important;
        margin-bottom: 25px;
        font-weight: 600;
        border: 1.5px solid #475569;
        border-top: 5px solid #3B82F6;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# LOGIN / REGISTRATION ROUTING
# =========================================================

if not st.session_state.logged_in:

    logo_path = "rcpit logo.jpg"
    logo_base64 = get_image_base64(logo_path)

    logo_img_tag = (
        f'<img src="data:image/png;base64,{logo_base64}" style="width: 55px;'
        ' height: 55px; object-fit: contain;" />'
        if logo_base64
        else '<span style="font-size: 2.2rem;">🎓</span>'
    )

    st.markdown(
        f"""
    <div class="enterprise-header">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="background: white; padding: 8px; border-radius: 10px; border: 1.5px solid #cbd5e1; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                {logo_img_tag}
            </div>
            <div>
                <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; color: #ffffff;">RCPIT CAMPUS CONNECT</div>
                <div style="font-size: 0.95rem; font-weight: 400; color: #cbd5e1; margin-top: 4px;">R. C. Patel Institute of Technology, Shirpur | Smart Academic Ecosystem & Community Hub</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.write("")  

    col_left, col_right = st.columns([1.1, 1.1], gap="large")

    with col_left:
        st.markdown(
            '<div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 15px;">📚 Welcome to Your Digital Campus</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size: 1.05rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 25px;">Empowering students and faculty with unified collaboration tools, technical societies, faculty mentorship, and streamlined campus interactions designed specifically for RCPIT.</div>',
            unsafe_allow_html=True,
        )

    with col_right:
        with st.container(border=True):

            # ---------------- 1. LOGIN MODE ---------------- #
            if st.session_state.auth_mode == "login":
                st.subheader("🔐Login Portal ")

                role = st.selectbox("Select Your Role", ["Student", "Faculty", "Club Leader"])

                if role in ["Student", "Faculty"]:
                    email = st.text_input("Email Address", placeholder="user@rcpit.ac.in")
                    password = st.text_input("Password", type="password", placeholder="••••••••")

                    if st.button(
                        f"Login as {role}", type="primary", use_container_width=True
                    ):
                        if not email or not password:
                            st.warning("Please fill in all required fields.")
                        else:
                            user = auth.login_user(role, email, password)
                            if user:
                                st.session_state.logged_in = True
                                st.session_state.role = role
                                st.session_state.name = user.get("full_name", "User")
                                st.session_state.user_data = user
                                st.success("Login Successful!")
                                st.rerun()
                            else:
                                st.error("Invalid Email or Password.")

                elif role == "Club Leader":
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT id, name FROM clubs")
                        all_clubs = cursor.fetchall()
                        conn.close()
                    except Exception:
                        all_clubs = []

                    if not all_clubs:
                        st.info(
                            "No registered clubs found yet. Click 'Register New Club' below"
                            " to create one!"
                        )
                    else:
                        club_options = {c["name"]: c["id"] for c in all_clubs}
                        selected_club_name = st.selectbox(
                            "Select Your Club", list(club_options.keys())
                        )
                        passcode = st.text_input("Enter Secret Leader Passcode", type="password", placeholder="••••••••")

                        if st.button(
                            "Login as Club Leader", type="primary", use_container_width=True
                        ):
                            if not passcode:
                                st.warning("Please enter your passcode.")
                            else:
                                try:
                                    conn = get_db_connection()
                                    cursor = conn.cursor(dictionary=True)
                                    cursor.execute(
                                        "SELECT * FROM clubs WHERE id = %s AND passcode = %s",
                                        (club_options[selected_club_name], passcode),
                                    )
                                    verified_club = cursor.fetchone()
                                    conn.close()

                                    if verified_club:
                                        st.session_state.logged_in = True
                                        st.session_state.role = "Club Leader"
                                        st.session_state.name = verified_club.get(
                                            "lead_name", "Leader"
                                        )
                                        st.session_state.user_data = verified_club
                                        st.success(f"Welcome Leader of {selected_club_name}!")
                                        st.rerun()
                                    else:
                                        st.error("Incorrect Passcode!")
                                except Exception as e:
                                    st.error(f"Login Error: {e}")

                st.markdown("---")
                if role == "Student":
                    st.write("New to Campus Connect?")
                    if st.button("Create Student Account", use_container_width=True):
                        st.session_state.auth_mode = "register_student"
                        st.rerun()

                elif role == "Faculty":
                    st.write("Joining as Faculty Member?")
                    if st.button("Register Faculty Account", use_container_width=True):
                        st.session_state.auth_mode = "register_faculty"
                        st.rerun()

                elif role == "Club Leader":
                    st.write("Want to Register a New Campus Club?")
                    if st.button("Register New Club", use_container_width=True):
                        st.session_state.auth_mode = "register_club"
                        st.rerun()

            # ---------------- 2. STUDENT REGISTRATION ---------------- #
            elif st.session_state.auth_mode == "register_student":
                st.subheader("📝 Student Registration Portal")

                full_name = st.text_input("Full Name", placeholder="e.g. Dishant Pawar")
                reg_email = st.text_input("Email Address", placeholder="student@rcpit.ac.in")
                reg_password = st.text_input("Create Password", type="password", placeholder="••••••••")
                branch = st.selectbox(
                    "Select Branch",
                    [
                        "AI & ML",
                        "Computer Engineering",
                        "Data Science",
                        "IT",
                        "ENTC",
                        "Mechanical",
                        "Civil",
                    ],
                )
                year = st.selectbox(
                    "Select Academic Year",
                    [
                        "First Year (FE)",
                        "Second Year (SE)",
                        "Third Year (TE)",
                        "Final Year (BE)",
                    ],
                )

                if st.button(
                    "Submit & Register Student", type="primary", use_container_width=True
                ):
                    if not full_name or not reg_email or not reg_password:
                        st.error("Please fill all required fields.")
                    else:
                        success, message = auth.register_student(
                            full_name=full_name,
                            email=reg_email,
                            password=reg_password,
                            branch=branch,
                            year=year,
                        )
                        if success:
                            st.success(message)
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(message)

                st.markdown("---")
                if st.button(
                    "← Already have an account? Login", use_container_width=True
                ):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            # ---------------- 3. FACULTY REGISTRATION PORTAL ---------------- #
            elif st.session_state.auth_mode == "register_faculty":
                st.subheader("👨‍🏫 Faculty Registration Portal")

                full_name = st.text_input("Full Name", placeholder="e.g. Dr. Faculty Name")
                reg_email = st.text_input("Faculty Email Address", placeholder="faculty@rcpit.ac.in")
                reg_password = st.text_input("Create Password", type="password", placeholder="••••••••")
                department = st.selectbox(
                    "Select Department",
                    [
                        "AI & ML",
                        "Computer Engineering",
                        "Data Science",
                        "IT",
                        "ENTC",
                        "Mechanical",
                        "Civil",
                    ],
                )
                designation = st.selectbox(
                    "Designation",
                    [
                        "Assistant Professor",
                        "Associate Professor",
                        "Professor",
                        "Head of Department (HOD)",
                    ],
                )

                if st.button(
                    "Submit & Register Faculty", type="primary", use_container_width=True
                ):
                    if not full_name or not reg_email or not reg_password:
                        st.error("Please fill all required fields.")
                    else:
                        if hasattr(auth, "register_faculty"):
                            success, message = auth.register_faculty(
                                full_name=full_name,
                                email=reg_email,
                                password=reg_password,
                                department=department,
                                designation=designation,
                            )
                        else:
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO faculty (full_name, email, password,"
                                    " department, designation) VALUES (%s, %s, %s, %s, %s)",
                                    (
                                        full_name.strip(),
                                        reg_email.strip(),
                                        reg_password.strip(),
                                        department,
                                        designation,
                                    ),
                                )
                                conn.commit()
                                conn.close()
                                success, message = (
                                    True,
                                    "Faculty Account Registered Successfully!",
                                )
                            except Exception as err:
                                success, message = False, f"Database Error: {err}"

                        if success:
                            st.success(message)
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(message)

                st.markdown("---")
                if st.button(
                    "← Already have an account? Login", use_container_width=True
                ):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            # ---------------- 4. CLUB REGISTRATION PORTAL ---------------- #
            elif st.session_state.auth_mode == "register_club":
                st.subheader("🎪 Register New Campus Club")
                st.caption("Fill in details to set up your club and leader credentials.")

                club_name = st.text_input(
                    "Club Name", placeholder="e.g. AI & Robotics Club, Coding Society"
                )
                category = st.selectbox(
                    "Category",
                    ["Technical", "Cultural", "Sports", "Literature", "Social", "Other"],
                )
                lead_name = st.text_input("Leader Name", placeholder="e.g. Dishant Pawar")
                lead_email = st.text_input("Leader Email", placeholder="leader@rcpit.ac.in")
                passcode = st.text_input("Set Secret Leader Passcode", type="password", placeholder="••••••••")
                description = st.text_area(
                    "Club Description",
                    placeholder="Brief description about activities, vision, and events...",
                )

                if st.button(
                    "🚀 Create & Register Club", type="primary", use_container_width=True
                ):
                    if (
                        not club_name
                        or not lead_name
                        or not passcode
                        or not description
                    ):
                        st.warning("Please fill in all required fields!")
                    else:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO clubs (name, category, lead_name, lead_email,"
                                " passcode, description) VALUES (%s, %s, %s, %s, %s, %s)",
                                (
                                    club_name.strip(),
                                    category,
                                    lead_name.strip(),
                                    lead_email.strip(),
                                    passcode.strip(),
                                    description.strip(),
                                ),
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"🎉 '{club_name}' Registered Successfully!")
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        except mysql.connector.Error as err:
                            if err.errno == 1062:
                                st.error(f"A club named '{club_name}' already exists!")
                            else:
                                st.error(f"Error registering club: {err}")

                st.markdown("---")
                if st.button("← Back to Login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()

# =========================================================
# DASHBOARD ROUTING (LOGGED IN USER)
# =========================================================

else:

    if st.session_state.role == "Student":
        show_student_dashboard()

    elif st.session_state.role == "Faculty":
        try:
            show_faculty_dashboard(st.session_state.user_data)
        except TypeError:
            show_faculty_dashboard()

    elif st.session_state.role == "Club Leader":
        try:
            show_leader_dashboard(st.session_state.user_data)
        except TypeError:
            show_leader_dashboard()

  