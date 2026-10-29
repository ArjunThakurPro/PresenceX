import streamlit as st
from src.database.config import supabase
from src.database.db import student_enroll


@st.dialog("Join a subject", width="small", icon=":material/school:")
def subject_joining(subject_code):
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
    student_id = st.session_state.student_data["student_id"]
    subject_code = subject_code.strip()
    if not subject_code:
        st.error("This subject invitation is missing a subject code.")
        return
    if supabase is None:
        st.error("Enrollment is currently unavailable. Please try again later.")
        return

    res = (
        supabase.table("subjects")
        .select("subject_id, name")
        .eq("subject_code", subject_code)
        .execute()
    )
    if not res.data:
        st.error("We couldn't find a subject with this invitation code.")
        if st.button(
            "Close invitation",
            type="secondary",
            icon=":material/close:",
            width="stretch",
        ):
            st.query_params.clear()
            st.rerun()
        return
    subject = res.data[0]
    check = (
        supabase.table("subject__student")
        .select("student_id")
        .eq("subject_id", subject["subject_id"])
        .eq("student_id", student_id)
        .execute()
    )
    if check.data:
        st.info("You're already enrolled in this subject.")
        if st.button(
            "Got it",
            type="secondary",
            icon=":material/check:",
            width="stretch",
        ):
            st.query_params.clear()
            st.rerun()
        return

    st.caption("A class invitation is ready for you.")
    with st.container(border=True):
        st.caption("SUBJECT")
        st.subheader(subject["name"])
        st.write("Would you like to join this subject?")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button(
            "Not now",
            type="secondary",
            icon=":material/close:",
            width="stretch",
        ):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button(
            "Join subject",
            type="primary",
            icon=":material/check:",
            width="stretch",
        ):
            if student_enroll(subject["subject_id"], student_id):
                st.success("You're enrolled. Welcome to the subject!")
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Enrollment could not be completed. Please try again.")
