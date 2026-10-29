import streamlit as st


def header_logo():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image("PresenceX.png", width=300)


def header_dashboard():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image("PresenceX.png", width=250)
