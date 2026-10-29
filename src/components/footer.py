import streamlit as st


def home_footer():
    st.markdown(
        f"""
        <div style= "margin-top:5rem; display: flex; gap:6px; justify-content: center; align-items: center;">
        
        <marque><p style= "font-weight: bold; color:black;">Created with ❤️ by Arjun Rajput</p><marque>
        </div>
        """,
        unsafe_allow_html=True,
    )
