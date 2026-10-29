import streamlit as st
from PIL import Image
import time
from src.database.db import attendance_log_db


def _inject_attendance_dialog_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bitcount+Prop+Double+Ink:wght@100..900&display=swap');
        div[data-testid="stDialog"] h2 {
            color: #ffffff !important;
            font-family: "Bitcount Prop Double Ink", system-ui !important;
        }

        .attendance-dialog-shell {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.97), rgba(22, 38, 58, 0.97));
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 22px;
            padding: 1.5rem 1.5rem 1rem 1.5rem;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.35);
            margin-top: 0.25rem;
        }

        .attendance-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }

        .attendance-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(96, 165, 250, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.28);
            color: #bfdbfe;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .attendance-title {
            margin: 0.45rem 0 0.15rem 0;
            font-size: clamp(1.55rem, 2vw, 2.2rem);
            font-weight: 700;
            color: white;
            line-height: 1.2;
        }

        .attendance-subtitle {
            margin: 0 0 1rem 0;
            font-size: 0.96rem;
            color: white !important;
        }

        .attendance-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin: 0.5rem 0 1rem 0;
        }

        .attendance-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.18);
            color: #ccfbf1;
            border: 1px solid rgba(45, 212, 191, 0.2);
            font-size: 0.75rem;
            font-weight: 600;
        }

        .attendance-pill.accent {
            background: rgba(59, 130, 246, 0.12);
            color: #dbeafe;
            border-color: rgba(96, 165, 250, 0.25);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .stButton > button {
            border-radius: 12px;
            min-height: 2.9rem;
            padding: 0.6rem 1.3rem;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(15, 118, 110, 0.18);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #14b8a6, #0ea5e9);
            border: none;
            color: white !important;
        }

        .stButton > button[kind="secondary"] {
            background: rgba(148, 163, 184, 0.08);
            border: 1px solid rgba(148, 163, 184, 0.18);
            color: #e2e8f0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Attendance Catalogue")
def attendance_result_dialog(result, logs):
    _inject_attendance_dialog_styles()

    records_count = (
        len(result) if result is not None and hasattr(result, "__len__") else 0
    )

    st.markdown(
        """
        <div class="attendance-dialog-shell">
            <div class="attendance-header">
                <div>
                    <div class="attendance-badge">Attendance Review</div>
                    <h2 class="attendance-title">Attendance Catalogue</h2>
                </div>
            </div>
            <p class="attendance-subtitle">Please review your attendance before confirming.</p>
            <div class="attendance-meta">
                <span class="attendance-pill">Records: {count}</span>
                <span class="attendance-pill accent">Ready for confirmation</span>
            </div>
        </div>
        """.format(count=records_count),
        unsafe_allow_html=True,
    )

    st.dataframe(result, hide_index=True, width="stretch", use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(
            "Confirm & Save",
            type="primary",
            icon=":material/check_circle:",
        ):
            try:
                if not logs:
                    st.warning("No attendance logs available to save.")
                    return

                attendance_log_db(logs)
                st.session_state.attendance_image = []
                st.success("Attendance saved successfully.")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error("Failed to save attendance. Please try again.")
                st.exception(e)

    with col2:
        if st.button("Cancel", type="secondary", icon=":material/close:"):
            st.rerun()
