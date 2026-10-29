import bcrypt
import numpy as np
import streamlit as st
from src.database.config import supabase


def _safe_execute(query_builder):
    if query_builder is None:
        return None
    try:
        return query_builder.execute()
    except Exception:
        return None


def _to_json_safe(value):
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return _to_json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(item) for item in value]
    return value


def hash_pwd(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(user_name):
    if not user_name or supabase is None:
        return False
    try:
        response = _safe_execute(
            supabase.table("teachers").select("user_name").eq("user_name", user_name)
        )
        return bool(response and response.data)
    except Exception:
        return False


def create_teacher(user_name, password, name):
    if supabase is None:
        return None
    try:
        data = {"user_name": user_name, "password": hash_pwd(password), "name": name}
        response = _safe_execute(supabase.table("teachers").insert(data))
        return response
    except Exception:
        return None


def teacher_login(username, password):
    if not username or not password or supabase is None:
        return None
    try:
        response = _safe_execute(
            supabase.table("teachers").select("*").eq("user_name", username)
        )
        if response and response.data:
            teacher = response.data[0]
            if check_pass(password, teacher["password"]):
                return teacher
    except Exception:
        return None
    return None


def get_all_students():
    if supabase is None:
        return []
    try:
        subject_id = st.session_state.get("subject_id")
        if subject_id:
            enrollment_response = _safe_execute(
                supabase.table("subject__student")
                .select("student_id")
                .eq("subject_id", subject_id)
            )
            student_ids = [
                enrollment["student_id"]
                for enrollment in (
                    enrollment_response.data if enrollment_response else []
                )
                if enrollment.get("student_id") is not None
            ]
            if not student_ids:
                st.markdown(
                    """
                    <div style="
                        background-color: #fee2e2;
                        border: 1px solid #f87171;
                        border-radius: 0.5rem;
                        color: #b91c1c;
                        font-weight: 700;
                        padding: 0.75rem 1rem;
                    ">
                        No students are enrolled in this subject.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                return []

            response = _safe_execute(
                supabase.table("students").select("*").in_("student_id", student_ids)
            )
            return (response.data if response else []) or []

        response = _safe_execute(supabase.table("students").select("*"))
        return (response.data if response else []) or []
    except Exception:
        return []


def create_student(
    name,
    enrollment_no=None,
    face_embedding=None,
    face_embedding2=None,
    face_embedding3=None,
    face_embedding4=None,
    voice_embedding=None,
):
    if supabase is None:
        return None
    try:
        data = {
            "name": name,
            "Enrollment_No": enrollment_no,
            "face_embedding": _to_json_safe(face_embedding),
            "face_embedding2": face_embedding2,
            "face_embedding3": face_embedding3,
            "face_embedding4": face_embedding4,
            "voice_embedding": _to_json_safe(voice_embedding),
        }
        response = _safe_execute(supabase.table("students").insert(data))
        return response.data if response else None
    except Exception:
        return None


def insert_subject(subject_code, subject_name, program, section, teacher_id):
    if supabase is None:
        return None
    try:
        data = {
            "subject_code": subject_code,
            "name": subject_name,
            "Program": program,
            "section": section,
            "teacher_id": teacher_id,
        }
        response = _safe_execute(supabase.table("subjects").insert(data))
        return response.data if response else None
    except Exception:
        return None


def delete_subject(subject_id, teacher_id):
    if supabase is None:
        return False
    try:
        subject_response = _safe_execute(
            supabase.table("subjects")
            .select("subject_id")
            .eq("subject_id", subject_id)
            .eq("teacher_id", teacher_id)
        )
        if not subject_response or not subject_response.data:
            return False

        _safe_execute(
            supabase.table("subject__student").delete().eq("subject_id", subject_id)
        )
        _safe_execute(
            supabase.table("attendance_logs").delete().eq("subject_id", subject_id)
        )
        response = _safe_execute(
            supabase.table("subjects")
            .delete()
            .eq("subject_id", subject_id)
            .eq("teacher_id", teacher_id)
            .select("subject_id")
        )
        return bool(response and response.data)
    except Exception:
        return False


def get_teacher_subjects(teacher_id):
    if supabase is None:
        return [], [], []
    try:
        subjects_response = _safe_execute(
            supabase.table("subjects").select("*").eq("teacher_id", teacher_id)
        )
        subjects = (subjects_response.data if subjects_response else []) or []
        total_students = []
        total_class = []

        for subject in subjects:
            subject_id = subject.get("subject_id")
            if subject_id is None:
                continue

            students_response = _safe_execute(
                supabase.table("subject__student")
                .select("student_id, subject_id")
                .eq("subject_id", subject_id)
            )
            total_students.extend(
                (students_response.data if students_response else []) or []
            )

            classes_response = _safe_execute(
                supabase.table("attendance_logs")
                .select("timestamp, subject_id")
                .eq("subject_id", subject_id)
            )
            total_class.extend(
                (classes_response.data if classes_response else []) or []
            )

        return subjects, total_students, total_class
    except Exception:
        return [], [], []


def student_enroll(subject_id, student_id):
    if supabase is None:
        return None
    try:
        data = {"subject_id": subject_id, "student_id": student_id}
        response = _safe_execute(supabase.table("subject__student").insert(data))
        return response.data if response else None
    except Exception:
        return None


def get_subject_id(student_id):
    if supabase is None:
        return None
    try:
        response = _safe_execute(
            supabase.table("subject__student")
            .select("subject_id")
            .eq("student_id", student_id)
        )
        return response.data[0]["subject_id"] if response and response.data else None
    except Exception:
        return None


def student_unenroll(subject_id, student_id):
    if supabase is None:
        return None
    try:
        response = _safe_execute(
            supabase.table("subject__student")
            .delete()
            .eq("student_id", student_id)
            .eq("subject_id", subject_id)
            .select("student_id")
        )
        return response.data if response else None
    except Exception:
        return None


def get_student_subjects(student_id):
    if supabase is None:
        return []
    try:
        response = _safe_execute(
            supabase.table("subject__student")
            .select("*, subjects(*)")
            .eq("student_id", student_id)
        )
        return (response.data if response else []) or []
    except Exception:
        return []


def get_student_attendance(student_id):
    if supabase is None:
        return []
    try:
        response = _safe_execute(
            supabase.table("attendance_logs")
            .select("*, subjects(*)")
            .eq("student_id", student_id)
        )
        return (response.data if response else []) or []
    except Exception:
        return []


def student_attendance(student_id):
    return get_student_attendance(student_id)


def teacher_subjects(teacher_id):
    if supabase is None:
        return []
    try:
        response = _safe_execute(
            supabase.table("subjects").select("*").eq("teacher_id", teacher_id)
        )
        return (response.data if response else []) or []
    except Exception:
        return []


def attendance_log_db(log):
    response = supabase.table("attendance_logs").insert(log).execute()
    return response.data
