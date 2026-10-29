import streamlit as st
from src.components.footer import home_footer
from src.database.config import supabase
import time
from src.database.db import student_enroll


@st.dialog("Enroll Subject")
def subject_enrollment(student_id):
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
    subject_code = st.text_input("Enter Subject Code", placeholder="Subject Code")
    if st.button("Enroll", width="stretch", type="secondary"):
        subject_code = subject_code.strip()
        if not subject_code:
            st.warning("Enter a subject code to enroll.")
        else:
            response = (
                supabase.table("subjects")
                .select("subject_id, name")
                .eq("subject_code", subject_code)
                .execute()
            )
            if not response.data:
                st.error("No subject was found with that code.")
            else:
                subject_id = response.data[0]["subject_id"]
                subject_name = response.data[0]["name"]
                student_check = (
                    supabase.table("subject__student")
                    .select("student_id")
                    .eq("subject_id", subject_id)
                    .eq("student_id", student_id)
                    .execute()
                )
                if student_check.data:
                    st.warning(f"You are already enrolled in {subject_name}.")
                else:
                    with st.spinner("Enrolling..."):
                        response = student_enroll(subject_id, student_id)
                        if response:
                            st.success(
                                f"You are successfully enrolled in {subject_name}!"
                            )
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(
                                "Enrollment could not be completed. Please try again."
                            )
