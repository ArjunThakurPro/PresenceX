import streamlit as st
from src.components.header import header_logo
from src.components.footer import home_footer
from src.ui.base_layout import (
    style_background_home,
    style_background_dashboard,
    style_base_layout,
)


def home():
    # st.header("Home")
    header_logo()
    # st.image("AttendVision Logo.png", width=220)
    style_background_home()
    style_base_layout()
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(key="teacher_card"):
            st.header("I am Teacher..")
            st.image("teacher_2.webp", width=200)
            if st.button("Teacher Portal", type="primary", key="bt1", width="stretch"):
                st.session_state["login_type"] = "Teacher"
                st.rerun()
    with col2:
        with st.container(key="student_card"):
            st.header("I am Student..")
            st.image("student.png", width=210)
            if st.button("Student Portal", type="primary", key="bt2", width="stretch"):
                st.session_state["login_type"] = "Student"
                st.rerun()

    home_footer()
