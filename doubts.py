import streamlit as st


def show_doubt_forum_page():
    st.title("💬 Student Doubt Forum")
    st.caption("Ask questions, clear your concepts, and view answers from faculty members.")
    st.markdown("---")

    st.error("🚧 **MODULE UNDER MAINTENANCE**")

    with st.container(border=True):
        st.markdown("### ⚠️ System Maintenance Notice")
        st.write(
            "The Student Doubt Forum is currently offline for scheduled database migrations, "
            "UI enhancements, and faculty response workflow upgrades."
        )
        st.info(
            "**Status:** All question submission and review endpoints are temporarily suspended "
            "for maintenance. Please check back shortly."
        )