from functools import partial
import pandas as pd
from src.components.share_QR import share_qr_code
import streamlit as st
from postgrest.exceptions import APIError
from src.components.footer import home_footer
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.components.subject_creation import create_subject
from src.database.db import teacher_subjects
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    delete_subject,
    get_teacher_subjects,
    teacher_login,
)
from src.pipelines.face_pipeline import predict_attendence
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
    style_teacher_dashboard,
)
from src.components.dialog_add_photos import add_photo_dialog
from src.database.config import supabase
from datetime import datetime
from src.components.attendance_dialog import attendance_result_dialog
from src.components.Students_presences import students_presence_report


def teacher():
    style_background_dashboard()
    style_base_layout()
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    else:
        teacher_screen_login()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    style_teacher_dashboard()

    with st.container(key="teacher_dashboard"):
        with st.container(key="teacher_hero"):
            brand_col, welcome_col, action_col = st.columns(
                [1.1, 3.2, 2], vertical_alignment="center", gap="large"
            )
            with brand_col:
                st.image("PresenceX.png", width=160)
            with welcome_col:
                st.caption("TEACHER WORKSPACE")
                st.title(f"Welcome back, {teacher_data['name']}!")
                st.caption("Your classes, attendance, and subjects—all in one place.")
            with action_col, st.container(key="teacher_actions"):
                if st.button(
                    "Home",
                    icon=":material/home:",
                    shortcut="control+backspace",
                    key="bt1",
                    width="stretch",
                    type="secondary",
                ):
                    st.session_state["login_type"] = None
                    st.rerun()
                if st.button(
                    "Logout",
                    icon=":material/logout:",
                    key="bt2",
                    width="stretch",
                    type="secondary",
                ):
                    st.session_state.is_logged_in = False
                    del st.session_state.teacher_data
                    st.rerun()

        st.write("")
        if "current_teacher_tab" not in st.session_state:
            st.session_state.current_teacher_tab = "take_attendance"
        with st.container(key="teacher_navigation"):
            tab1, tab2, tab3 = st.columns(3, gap="medium")
            with tab1:
                type1 = (
                    "primary"
                    if st.session_state.current_teacher_tab == "take_attendance"
                    else "secondary"
                )
                if st.button(
                    "Take Attendance",
                    width="stretch",
                    icon=":material/camera:",
                    type=type1,
                    key="teacher_tab_attendance",
                ):
                    st.session_state.current_teacher_tab = "take_attendance"
                    st.rerun()
            with tab2:
                type2 = (
                    "primary"
                    if st.session_state.current_teacher_tab == "my_subject"
                    else "secondary"
                )
                if st.button(
                    "My Subjects",
                    width="stretch",
                    icon=":material/book:",
                    type=type2,
                    key="teacher_tab_subjects",
                ):
                    st.session_state.current_teacher_tab = "my_subject"
                    st.rerun()
            with tab3:
                type3 = (
                    "primary"
                    if st.session_state.current_teacher_tab == "attendance_report"
                    else "secondary"
                )
                if st.button(
                    "Attendance Report",
                    width="stretch",
                    icon=":material/calendar_today:",
                    type=type3,
                    key="teacher_tab_report",
                ):
                    st.session_state.current_teacher_tab = "attendance_report"
                    st.rerun()

        with st.container(key="teacher_content"):
            if st.session_state.current_teacher_tab == "take_attendance":
                teacher_take_attendance()
            elif st.session_state.current_teacher_tab == "my_subject":
                my_subject()
            elif st.session_state.current_teacher_tab == "attendance_report":
                attendance_report()

    home_footer()


def teacher_take_attendance():
    st.header("Take AI Attendance")
    if "attendance_image" not in st.session_state:
        st.session_state.attendance_image = []
    teacher_id = st.session_state.teacher_data["teacher_id"]
    subjects = teacher_subjects(teacher_id)
    if not subjects:
        st.warning("You did not create any subject! create one to begin")
        return
    subject_options = {
        f"{s['name']}- {s['subject_code']}- Sec {s['section']}": s["subject_id"]
        for s in subjects
    }
    col1, col2 = st.columns([3, 1])
    with col1:
        subject_keys = st.selectbox(
            "Select Subject for Attendance", options=list(subject_options.keys())
        )
    with col2:
        if st.button(
            "Take Photo",
            type="primary",
            icon=":material/photo_camera:",
            width="stretch",
        ):
            add_photo_dialog()
    st.divider()
    selected_subject_id = subject_options[subject_keys]
    section = (
        supabase.table("subjects")
        .select("section")
        .eq("subject_id", selected_subject_id)
    )
    st.session_state.subject_id = selected_subject_id
    attendance_images = st.session_state.attendance_image
    if attendance_images:
        st.subheader("Photos captured this session")
        photo_columns = st.columns(3)
        for index, photo in enumerate(attendance_images):
            with photo_columns[index % len(photo_columns)]:
                st.image(photo, caption=f"Photo {index + 1}", width="stretch")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(
                "Clear All Photos",
                width="stretch",
                type="primary",
                icon=":material/delete:",
            ):
                st.session_state.attendance_image = []
                st.rerun()
        with c2:
            if st.button(
                "Analyse to Images",
                width="stretch",
                type="secondary",
                icon=":material/analytics:",
            ):
                with st.spinner("Deep Analysing"):
                    all_detected_id = {}
                    for img in st.session_state.attendance_image:
                        if img is None:
                            continue
                        detected_student, _, _ = predict_attendence(img)
                        if not detected_student:
                            continue
                        for student_id in detected_student:
                            all_detected_id[str(student_id)] = True

                    if not all_detected_id:
                        st.warning("No students detected in the uploaded images.")
                    else:
                        detected_ids = [
                            str(student_id) for student_id in all_detected_id
                        ]
                        st.success(
                            f"Attendance marked for {len(detected_ids)} students: {', '.join(detected_ids)}"
                        )

                    if supabase is None:
                        st.error(
                            "Database is unavailable. Attendance was not recorded."
                        )
                        return

                    enrolled_res = (
                        supabase.table("subject__student")
                        .select("*, students(*)")
                        .eq("subject_id", selected_subject_id)
                        .execute()
                    )
                    enrolled_student = enrolled_res.data if enrolled_res else []
                    if not enrolled_student:
                        st.warning("No one enrolled in this Course")
                    else:
                        results, attendance_log = [], []
                        current_time_stamp = datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )
                        detected_ids_set = set(
                            str(student_id) for student_id in all_detected_id
                        )
                        for node in enrolled_student:
                            student = node.get("students") or {}
                            raw_student_id = student.get("student_id")
                            if raw_student_id is None:
                                continue
                            student_id = str(raw_student_id)
                            source = (
                                [student_id] if student_id in detected_ids_set else []
                            )
                            is_present = bool(source)
                            results.append(
                                {
                                    "Name": student.get("name") or "Unknown",
                                    "Enrollment No": student.get("Enrollment_No")
                                    or "-",
                                    "Sources": ", ".join(source) if is_present else "-",
                                    "Status": "✅Present" if is_present else "❌Absent",
                                }
                            )
                            attendance_log.append(
                                {
                                    "student_id": raw_student_id,
                                    "subject_id": selected_subject_id,
                                    "timestamp": current_time_stamp,
                                    "is_present": is_present,
                                }
                            )
                        if not results:
                            st.warning("No enrolled student records were found.")
                            return
                        attendance_result_dialog(pd.DataFrame(results), attendance_log)
        with c3:
            if st.button("Voice Attendance", width="stretch", icon=":material/mic:"):
                st.success("Under Development")


def take_attendance():
    st.header("Take Attendance")
    st.caption("Capture a class photo to identify students and record attendance.")
    faces = st.camera_input("Take a picture of the class to mark attendance")
    if faces:
        detected_student, _, _ = predict_attendence(faces)
        if detected_student:
            student_ids = [str(student_id) for student_id in detected_student]
            st.success(
                f"Attendance marked for {len(detected_student)} students: {', '.join(student_ids)}"
            )
        else:
            st.warning("No students detected in the image.")
    st.info("This feature is under development. Please check back later.")


@st.dialog("Delete Subject")
def _confirm_subject_deletion(subject_id, subject_name, teacher_id):
    st.warning(
        f"Delete **{subject_name or 'this subject'}**? This will also permanently "
        "delete its student enrollments and attendance records."
    )
    delete_col, cancel_col = st.columns(2)
    with delete_col:
        if st.button(
            "Delete",
            key=f"confirm_delete_subject_{subject_id}",
            icon=":material/delete:",
            type="primary",
            width="stretch",
        ):
            try:
                deleted = delete_subject(subject_id, teacher_id)
            except APIError:
                st.error("Could not delete this subject. Please try again.")
                return

            if not deleted:
                st.error(
                    "Subject not found or you do not have permission to delete it."
                )
                return

            st.toast("Subject deleted successfully.", icon=":material/delete:")
            st.rerun()
    with cancel_col:
        if st.button(
            "Cancel",
            key=f"cancel_delete_subject_{subject_id}",
            width="stretch",
        ):
            st.rerun()


def _render_delete_subject_button(subject_id, subject_name, teacher_id):
    if st.button(
        "Delete",
        key=f"delete_subject_{subject_id}",
        icon=":material/delete:",
        type="secondary",
        help="Delete this subject and its related records",
    ):
        _confirm_subject_deletion(subject_id, subject_name, teacher_id)


def _render_subject_actions(subject_id, subject_name, subject_code, teacher_id):
    _render_delete_subject_button(subject_id, subject_name, teacher_id)
    if subject_code and st.button(
        "Share Code",
        key=f"share_code_{subject_id}",
        width="stretch",
        icon=":material/share:",
    ):
        st.toast(f"Share this code with students: {subject_code}")
        share_qr_code(subject_name, subject_code)


def my_subject():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    with st.container(key="teacher_subject_header"):
        col1, col2 = st.columns([3, 1], vertical_alignment="center")
        with col1:
            st.header("Your Subjects")
            st.caption("Manage your classes and keep track of student activity.")
        with col2:
            if st.button(
                "Add Subject",
                type="primary",
                key="add_subject",
                icon=":material/add:",
                width="stretch",
            ):
                create_subject(teacher_id)
    st.divider()
    subjects, total_students, total_class = get_teacher_subjects(teacher_id)
    if not subjects:
        st.info("No subjects yet. Add your first subject to start organizing classes.")
        return

    student_counts = {}
    for row in total_students:
        subject_id = row.get("subject_id")
        student_counts[subject_id] = student_counts.get(subject_id, 0) + 1

    class_timestamps = {}
    for row in total_class:
        subject_id = row.get("subject_id")
        timestamp = row.get("timestamp")
        if subject_id is not None and timestamp is not None:
            class_timestamps.setdefault(subject_id, set()).add(timestamp)

    columns = st.columns(2, gap="medium")
    for index, subject in enumerate(subjects):
        subject_id = subject.get("subject_id")
        stats = [
            ("👨‍🎓", "Students", student_counts.get(subject_id, 0)),
            ("🕒", "Classes", len(class_timestamps.get(subject_id, set()))),
        ]
        with columns[index % 2]:
            subject_card(
                subject_name=subject.get("name"),
                subject_code=subject.get("subject_code"),
                program=subject.get("Program"),
                section=subject.get("section"),
                stats=stats,
                footer_callback=(
                    partial(
                        _render_subject_actions,
                        subject_id,
                        subject.get("name"),
                        subject.get("subject_code"),
                        teacher_id,
                    )
                    if subject_id is not None
                    else None
                ),
            )


def attendance_report():
    st.header("Attendance Report")
    st.caption("Review attendance trends and class summaries.")
    teacher_id = st.session_state.teacher_data["teacher_id"]
    subjects = teacher_subjects(teacher_id)
    if not subjects:
        st.warning("You did not create any subject! create one to begin")
        return
    subject_options = {
        f"{s['name']}- {s['subject_code']}- {s['section']}": s["subject_id"]
        for s in subjects
    }
    subject_key = st.selectbox("Select subject", options=list(subject_options))
    attendance_date = st.date_input("Date")
    students_presence_report(subject_options[subject_key], attendance_date)
    st.divider()


# jai shree Ram Jai Shree Ram jai Shree Ram Jai Shree Ram Jai Shree Ram ji shree Ram RAm RAm RAm Ram Ram RAm RAm RAm Ram Ram Ram RAm Ram Ram Ram Ram Ram Ram Ram Ram ram ram ram ram ram ram ram ram ram ram ram ram ram r
def login_teacher(user_name, password):
    if not user_name or not password:
        return False
    teacher = teacher_login(user_name, password)
    if teacher:
        st.session_state["login_type"] = "Teacher"
        st.session_state.teacher_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    style_background_dashboard()
    style_base_layout()
    col1, col2 = st.columns(2, gap="xxlarge", vertical_alignment="center")
    with col1:
        header_dashboard()
    with col2:
        if st.button("Back to home✈", shortcut="control+backspace", key="bt4"):
            st.session_state["login_type"] = None
            st.rerun()

    st.space()
    st.header("Login🛡️ using password")
    st.space()
    teacher_username = st.text_input("Enter Username", placeholder="Arjun Rajput")
    st.space()
    teacher_password = st.text_input("Enter Password", type="password")
    st.divider()
    btncl1, btncl2 = st.columns(2)
    with btncl1:
        if st.button("Login", type="primary", width="stretch", key="log"):
            if login_teacher(teacher_username, teacher_password):
                st.toast("Welcome Back!", icon="😊")
                import time

                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Username and Password")

    with btncl2:
        if st.button("Register instead", type="secondary", width="stretch", key="re"):
            st.session_state["login_type"] = "Register"
            st.rerun()
    home_footer()


def teacher_register(name, username, password, con_password):
    if not name or not username or not password or not con_password:
        return False, "All fields are required"
    if check_teacher_exists(username):
        return False, "Username Already exists"
    if password != con_password:
        return False, "Password doesn't match"
    try:
        if create_teacher(username, password, name) is None:
            return False, "Could not create the account. Please try again."
        return True, "Successfully created👨‍🔧! Login Now"
    except (TypeError, ValueError):
        return False, "Unexcepted Error‼"


def teacher_screen_register():
    style_background_dashboard()
    style_base_layout()
    col1, col2 = st.columns(2, gap="xxlarge", vertical_alignment="center")
    with col1:
        header_dashboard()
    with col2:
        if st.button("Back to home✈", shortcut="control+backspace", key="bt3"):
            st.session_state["login_type"] = None
            st.rerun()
    st.header("   Register your teacher profile👨‍⚖️")
    Name = st.text_input("Enter your name", placeholder="Arjun")
    User_name = st.text_input("Enter you user Id", placeholder="@arjun")
    password = st.text_input("Password", type="password")
    Con_password = st.text_input("Confirm Password", type="password")
    bcl1, bcl2 = st.columns(2)
    with bcl1:
        if st.button(
            "Register", type="primary", key="reg", shortcut="Ctrl+k", width="stretch"
        ):
            success, message = teacher_register(Name, User_name, password, Con_password)
            if success:
                st.success(message)
                import time

                time.sleep(1)
                st.session_state["login_type"] = "login"
                st.rerun()
            else:
                st.error(message)
    with bcl2:
        if st.button("Instead Login", type="secondary", key="logi", width="stretch"):
            st.session_state["login_type"] = "login"
            st.rerun()

    home_footer()
