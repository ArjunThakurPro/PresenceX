from datetime import datetime, time, timedelta

import pandas as pd
import streamlit as st

from src.database.config import supabase


def students_presence_report(subject_id, attendance_date):
    if supabase is None:
        st.error("Database is unavailable. Attendance could not be loaded.")
        return

    start_of_day = datetime.combine(attendance_date, time.min).isoformat()
    start_of_next_day = datetime.combine(
        attendance_date + timedelta(days=1), time.min
    ).isoformat()

    try:
        attendance_response = (
            supabase.table("attendance_logs")
            .select("student_id, is_present, timestamp")
            .eq("subject_id", subject_id)
            .gte("timestamp", start_of_day)
            .lt("timestamp", start_of_next_day)
            .order("timestamp")
            .execute()
        )
    except Exception as error:
        st.error("Could not load attendance records.")
        st.exception(error)
        return

    attendance_records = attendance_response.data or []
    session_timestamps = sorted(
        {
            record["timestamp"]
            for record in attendance_records
            if record.get("timestamp")
        }
    )
    if not session_timestamps:
        st.info("No attendance has been recorded for this subject on this date.")
        return

    def format_session_time(timestamp):
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime(
                "%I:%M:%S %p"
            )
        except ValueError:
            return timestamp

    session_options = {
        format_session_time(timestamp): timestamp for timestamp in session_timestamps
    }
    selected_time = st.selectbox("Class time", options=list(session_options))
    selected_timestamp = session_options[selected_time]

    try:
        roster_response = (
            supabase.table("subject__student")
            .select("student_id, students(name, Enrollment_No)")
            .eq("subject_id", subject_id)
            .execute()
        )
    except Exception as error:
        st.error("Could not load the enrolled students for this subject.")
        st.exception(error)
        return

    enrolled_students = roster_response.data or []
    if not enrolled_students:
        st.info("No students are enrolled in this subject.")
        return

    attendance_by_student = {
        record["student_id"]: record.get("is_present")
        for record in attendance_records
        if record.get("timestamp") == selected_timestamp
        and record.get("student_id") is not None
    }
    rows = []
    for enrollment in enrolled_students:
        student = enrollment.get("students") or {}
        student_id = enrollment.get("student_id")
        is_present = attendance_by_student.get(student_id)
        rows.append(
            {
                "Name": student.get("name") or "Unknown",
                "Enrollment No": student.get("Enrollment_No") or "-",
                "Status": (
                    "Present"
                    if is_present is True
                    else "Absent"
                    if is_present is False
                    else "Not recorded"
                ),
            }
        )

    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
