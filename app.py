
import streamlit as st

# Must run before importing modules that may use Streamlit.
st.set_page_config(
    page_title="PresenceX - Connecting Student Presence With AI",
    page_icon="PresenceX.png"
)

from src.Screens.home_screen import home
from src.Screens.student_screen import student
from src.Screens.teacher_screen import (
    teacher,
    teacher_screen_register,
    teacher_screen_login,
)
from src.components.auto_enrolling import subject_joining

try:
  def main():
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    login_type = st.session_state["login_type"]

    match login_type:
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
        case _:
            st.session_state["login_type"] = None
            st.rerun()

    join_code = st.query_params.get("share-code")

    if join_code:
        if st.session_state.get("login_type") != "Student":
            st.session_state["login_type"] = "Student"
            st.rerun()

        if (
            st.session_state.get("is_logged_in", False)
            and st.session_state.get("user_role") == "student"
        ):
            subject_joining(join_code)
except Exception:
    error_details = traceback.format_exc()
    print(error_details)
    st.error("PresenceX encountered a startup/runtime error.")
    st.code(error_details, language="python")


if __name__ == "__main__":
    main()
