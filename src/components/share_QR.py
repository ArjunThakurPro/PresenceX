import streamlit as st
import segno
import io
from src.ui.base_layout import dialog_dashboard, style_base_layout


@st.dialog(title="Share QR Code")
def share_qr_code(subject_name, subject_code):
    dialog_dashboard()
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bitcount+Ink:wght@100..900&display=swap');
        [data-testid="stDialog"] [role="dialog"] {
            background-color: #1E1B4B !important;
            color: #FFFFFF !important;
        }

        [data-testid="stDialog"] [role="dialog"] h1,
        [data-testid="stDialog"] [role="dialog"] h2 {
            color: #FFFFFF !important;
            font-family: 'Bitcount Ink', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    app_domain = "PresenceX-main.streamlit.app"
    URL = f"{app_domain}/?share-code={subject_code}"
    st.header(f"Scan QR Code for {subject_name}")
    qr = segno.make(URL)
    out = io.BytesIO()
    qr.save(out, kind="png", scale=10, dark="black", light="white", border=1)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Copy Link:** ")

        st.code(URL, language="text")
        st.code(subject_code, language="text")
        st.info("Copy link to share on whatsapp or Email")

    with col2:
        st.markdown("##Scan to Join")
        st.image(
            out.getvalue(),
            use_container_width=True,
            caption=f"QR Code for {subject_name}",
        )
