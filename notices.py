import os
import streamlit as st
# Make sure to import your get_db_connection function from your database helper file

def show_student_notices():
    st.title("📢 Campus Notice Board")
    st.markdown("---")
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM faculty_notices ORDER BY created_at DESC")
            notices = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not notices:
                st.info("No notices available at the moment.")
            else:
                for notice in notices:
                    with st.container(border=True):
                        st.subheader(f"📌 {notice['title']}")
                        st.caption(f"Posted on: {notice['created_at']} | By: **{notice.get('posted_by', 'Faculty')}**")
                        st.write(notice["description"])
                        
                        f_path = notice.get("file_path")
                        if f_path and os.path.exists(f_path):
                            original_filename = os.path.basename(f_path).split('_', 2)[-1]
                            with open(f_path, "rb") as f_obj:
                                st.download_button(
                                    label=f"📥 Download Attachment ({original_filename})",
                                    data=f_obj,
                                    file_name=original_filename,
                                    key=f"student_dl_notice_{notice['id']}"
                                )
    except Exception as e:
        st.error(f"Error loading notices: {e}")