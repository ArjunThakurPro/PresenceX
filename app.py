import streamlit as st
from src.Screens.home_screen import home
from src.Screens.student_screen import student
from src.Screens.teacher_screen import (
    teacher,
    teacher_screen_register,
    teacher_screen_login,
)
from src.components.auto_enrolling import subject_joining


def main():
    st.set_page_config(
        page_title="PresenceX - Connecting Student Presence With AI",
        page_icon="http://localhost:8501/media/a8ec0894daa24aef744b3978da725720.png",
    )
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None
    match st.session_state["login_type"]:
        case "Teacher":
            teacher()
        case "Student":
            student()
        case None:
            home()
        case "Register":
            teacher_screen_register()
        case "login":
            teacher_screen_login()
    join_code = st.query_params.get("share-code")
    if join_code:
        if st.session_state["login_type"] != "Student":
            st.session_state["login_type"] = "Student"
            st.rerun()
        if (
            st.session_state["is_logged_in"]
            and st.session_state["user_role"] == "student"
        ):
            subject_joining(join_code)


main()
