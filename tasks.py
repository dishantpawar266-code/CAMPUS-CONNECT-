import mysql.connector
import streamlit as st


# --- DIRECT MYSQL CONNECTION ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="3251", database="campusconnect"
    )


# --- DB FUNCTIONS ---
def fetch_tasks(user_email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM tasks WHERE user_email = %s ORDER BY id DESC",
            (user_email,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"DB Error: {e}")
        return []


def add_task(user_email, title, time_slot):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (user_email, title, time_slot, is_completed)"
            " VALUES (%s, %s, %s, %s)",
            (user_email, title, time_slot, False),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error adding task: {e}")


def toggle_task(task_id, current_status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET is_completed = %s WHERE id = %s",
            (not current_status, task_id),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error updating task: {e}")


def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error deleting task: {e}")


# --- PAGE UI ---
def show_task_planner_page():
    st.title("📅 Task Planner")
    st.caption(
        "Apne daily tasks plan karein, time set karein aur completion track"
        " karein."
    )
    st.markdown("---")

    user_email = st.session_state.get("user_data", {}).get(
        "email"
    ) or st.session_state.get("email", "")

    if not user_email:
        st.warning("User email missing. Please login again.")
        return

    with st.form("add_task_form", clear_on_submit=True):
        st.subheader("➕ Add New Task")
        col_task, col_time = st.columns([3, 2])

        with col_task:
            new_title = st.text_input(
                "Task Description",
                placeholder="e.g., Solve Vector Calculus Sheet",
            )
        with col_time:
            new_time = st.text_input("Assign Time", placeholder="e.g., 10:30 AM")

        submit_btn = st.form_submit_button(
            "➕ Add Task", type="primary", use_container_width=True
        )

        if submit_btn:
            if new_title.strip() and new_time.strip():
                add_task(user_email, new_title.strip(), new_time.strip())
                st.success("Task Added!")
                st.rerun()
            else:
                st.warning("⚠️ Task aur Time dono bharo!")

    st.markdown("---")
    st.subheader("📋 Your Daily Schedule")

    tasks = fetch_tasks(user_email)

    if not tasks:
        st.info("Abhi koi task plan nahi kiya gaya hai.")
    else:
        for task in tasks:
            with st.container(border=True):
                col_chk, col_info, col_del = st.columns([1, 8, 1])

                with col_chk:
                    is_done = st.checkbox(
                        "",
                        value=bool(task["is_completed"]),
                        key=f"chk_{task['id']}",
                        label_visibility="collapsed",
                    )
                    if is_done != bool(task["is_completed"]):
                        toggle_task(task["id"], task["is_completed"])
                        st.rerun()

                with col_info:
                    if task["is_completed"]:
                        st.markdown(
                            f"~⏰ **[{task['time_slot']}]** {task['title']}~"
                            " *(Completed)*"
                        )
                    else:
                        st.markdown(
                            f"⏰ **[{task['time_slot']}]** {task['title']}"
                        )

                with col_del:
                    if st.button("🗑️", key=f"del_{task['id']}"):
                        delete_task(task["id"])
                        st.rerun()