import streamlit as st
from src.database.db import insert_subject
from src.ui.base_layout import style_base_layout, style_background_dashboard


@st.dialog("Create Subject")
def create_subject(teacher_id):
    teacher_id = teacher_id  # Use the passed teacher_id
    st.markdown(
        """
        <style>
        [data-testid="stDialog"] [role="dialog"] {
            background-color: #1E1B4B !important;
            color: #F8FAFC !important;
        }

        [data-testid="stDialog"] [role="dialog"] h1,
        [data-testid="stDialog"] [role="dialog"] h2,
        [data-testid="stDialog"] [role="dialog"] label,
        [data-testid="stDialog"] [role="dialog"] p {
            color: #F8FAFC !important;
        }

        [data-testid="stDialog"] [role="dialog"] div[data-baseweb="input"],
        [data-testid="stDialog"] [role="dialog"] div[data-baseweb="select"] > div {
            background-color: #3730A3 !important;
        }

        [data-testid="stDialog"] [role="dialog"] input,
        [data-testid="stDialog"] [role="dialog"] [data-baseweb="select"] span {
            color: #FFFFFF !important;
        }

        [data-testid="stDialog"] [role="dialog"] input::placeholder {
            color: #C7D2FE !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.form("create_subject_form"):
        style_base_layout()
        style_background_dashboard()
        subject_code = st.text_input("Subject Code", placeholder="BCA101")
        subject_name = st.text_input("Subject Name 📚", placeholder="Machine Learning")
        program = st.text_input("Program Or Class", placeholder="BCA")
        section = st.selectbox("Section", ["A", "B", "C", "D"], index=0)
        if st.form_submit_button(
            "Create Subject", type="secondary", icon=":material/add:"
        ):
            if subject_name and program:
                if insert_subject(
                    subject_code, subject_name, program, section, teacher_id
                ):
                    st.success(f"Subject {subject_name} created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create subject.")
            else:
                st.error("Subject Name and Program Name are mandatory.")
