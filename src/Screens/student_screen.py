import streamlit as st
from src.components.footer import home_footer
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
import numpy as np
from PIL import Image
from src.pipelines.face_pipeline import predict_attendence
from src.database.db import get_all_students, create_student
import time
from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import voice_embedding, identify_voice
from src.components.subject_enrolling import subject_enrollment
from src.components.subject_card import subject_card
from src.database.db import get_student_subjects, get_student_attendance
from src.database.db import student_unenroll
from src.components.photo_uploading import image_saving
import cv2


def _resolve_student_by_id(student_id):
    if student_id is None:
        return None
    all_students = get_all_students() or []
    for student in all_students:
        if student.get("student_id") == student_id:
            return student
    return None


def _get_student_session_data():
    for key in ("student_data", "user_data"):
        student_data = st.session_state.get(key)
        if (
            isinstance(student_data, dict)
            and student_data.get("student_id") is not None
            and student_data.get("student_id") != ""
        ):
            return student_data
    return None


def _resolve_student_by_voice(audio_embedding):
    if audio_embedding is None:
        return None

    all_students = get_all_students() or []
    best_match = None
    best_score = -1.0

    for student in all_students:
        voice_embedding_value = student.get("voice_embedding")
        if not voice_embedding_value:
            continue

        try:
            stored_embedding = np.asarray(voice_embedding_value, dtype=float)
            student_id = student.get("student_id")
            matched_student_id, score = identify_voice(
                audio_embedding, {student_id: stored_embedding}, 0.65
            )
            if matched_student_id and score > best_score:
                best_match = student
                best_score = score
        except (TypeError, ValueError):
            continue

    return best_match


def _login_student_photo(photo):
    if photo is None:
        return None
    try:
        img = Image.open(photo)
    except Exception:
        st.warning("Unable to read the selected photo. Please try again.")
        return None

    with st.spinner("AI is Scanning...."):
        detected, _all_ids, num_faces = predict_attendence(img)
        if num_faces == 0:
            st.warning("No face found")
            return None
        if num_faces > 1:
            st.warning("Multiple faces found")
            return None
        if not detected:
            st.info("Face not recognized! You might be a new student")
            return None

        student_id = next(iter(detected.keys()))
        student = _resolve_student_by_id(student_id)
        if student:
            st.header(f"Welcome back, {student.get('name', 'Student')}!")
            return student

    return None


def student():
    style_base_layout()
    style_background_dashboard()

    if "show_registration" not in st.session_state:
        st.session_state["show_registration"] = False

    student_data = _get_student_session_data()
    if student_data is not None:
        st.session_state["student_data"] = student_data
        student_dashboard()
        return

    if (
        st.session_state.get("student_data") is not None
        or st.session_state.get("user_data") is not None
    ):
        st.warning("Your student session is invalid. Please log in again.")
        st.session_state["student_data"] = None
        st.session_state["user_data"] = None
        st.session_state["is_logged_in"] = False
        st.session_state["user_role"] = None

    # ✅ FIX: enter registration mode once and return early so Streamlit does not render
    # the same form twice in a single rerun.
    if st.session_state.get("show_registration"):
        register_student()
        return

    st.markdown(
        """
        <style>
        .st-key-student_login_page {
            max-width: 900px;
            margin: 0 auto;
            padding: 0.5rem 0.25rem 2rem;
        }
        .st-key-student_login_card {
            padding: clamp(1.25rem, 4vw, 2.5rem);
            margin: 1.5rem auto;
            background: linear-gradient(145deg, #ffffff 0%, #f5f3ff 100%);
            border: 1px solid #e0defa;
            border-radius: 28px;
            box-shadow: 0 18px 45px rgba(65, 56, 150, 0.14);
        }
        .st-key-student_login_card h1,
        .st-key-student_login_card h2 {
            color: #25205f !important;
            text-align: center;
        }
        .st-key-student_login_card [data-testid="stCaptionContainer"] p {
            color: green !important;
            text-align: center;
        }
        .st-key-student_login_card [data-testid="stCameraInput"] {
            padding: 0.75rem;
            background: #f8f7ff;
            border: 1px dashed #aaa4ed;
            border-radius: 18px;
        }
        .st-key-student_login_card [data-testid="stAudioInput"] {
            padding: 0.75rem;
            background: #f8f7ff;
            border: 1px solid #e0defa;
            border-radius: 18px;
        }
        .st-key-student_login_page button[kind="primary"],
        .st-key-student_login_page button[kind="secondary"] {
            min-height: 2.8rem;
            border-radius: 16px !important;
            font-weight: 650 !important;
        }
        .st-key-student_login_page button[kind="primary"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, #625bf6, #4841c8) !important;
            border: 1px solid #5149dc !important;
            box-shadow: 0 8px 18px rgba(79, 70, 229, 0.2) !important;
        }
        .st-key-student_login_page button[kind="secondary"] {
            color: #443da7 !important;
            background: #ffffff !important;
            border: 1px solid #deddf8 !important;
        }
        .st-key-student_login_page [data-testid="stAlert"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="student_login_page"):
        col1, col2 = st.columns(
            2,
            vertical_alignment="center",
            gap="xxlarge",
        )
        with col1:
            header_dashboard()
        with col2:
            if st.button(
                "Back to Home✈",
                type="secondary",
                key="btt1",
                shortcut="control+backspace",
            ):
                st.session_state["login_type"] = None
                st.rerun()

        with st.container(key="student_login_card"):
            st.title("Welcome back")
            st.caption("Sign in securely with your face or voice.")
            photo = st.camera_input(
                "Position your face in the center", key="student_login_photo"
            )
            st.divider()
            st.caption("VoiceID is optional")
            audio_data = st.audio_input(
                "Loging uging VoiceID (Optional)", key="student_login_audio"
            )

            matched_student = _login_student_photo(photo)
            if audio_data:
                try:
                    audio_embedding = voice_embedding(audio_data)
                    voice_match = _resolve_student_by_voice(audio_embedding)
                    if voice_match:
                        matched_student = voice_match
                except Exception:
                    st.info("Voice recognition failed. Please try again.")

            if matched_student:
                st.session_state.is_logged_in = True
                st.session_state.user_role = "student"
                st.session_state.user_data = matched_student
                st.session_state.student_data = matched_student
                st.session_state["login_type"] = "Student"
                st.toast(f"welcome back {matched_student.get('name', 'Student')}")
                time.sleep(1)
                st.rerun()

            if audio_data and not matched_student:
                st.info(
                    "Face not recognized! You might be a new student, You need to register first or try again with a different voice sample."
                )

            st.divider()
            if st.button(
                "Register",
                type="primary",
                width="stretch",
                key="student_register_open",
            ):
                st.session_state["show_registration"] = True
                st.rerun()


@st.dialog("Delete Subject")
def confirm_enrollment_deletion(subject_id, student_id):
    st.warning(
        "Remove this subject from your enrolled subjects? This does not delete "
        "the subject or its attendance records."
    )
    delete_col, cancel_col = st.columns(2)
    with delete_col:
        if st.button(
            "Delete",
            key=f"confirm_unenrollment_{subject_id}",
            icon=":material/delete:",
            type="primary",
            width="stretch",
        ):
            try:
                deleted = student_unenroll(subject_id, student_id)
            except Exception:
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


def register_student():
    if "saving" not in st.session_state:
        st.session_state.photo_tab = "Photo"

    st.markdown(
        """
        <style>
        h1, h2, h3 {
            color: #111827 !important;
            background: linear-gradient(90deg, #dbeafe, #eff6ff);
            border-left: 5px solid #3b82f6;
            border-radius: 0.75rem;
            padding: 0.55rem 0.85rem;
        }
        [data-testid="stCaptionContainer"] p {
            color: green !important;
        }
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            color: #dc2626 !important;
            font-weight: 700 !important;
        }
        [data-testid="stProgress"] p,
        [data-testid="stImage"] p {
            color: #dc2626 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        title_col, back_col = st.columns([4, 1], vertical_alignment="center")
        with title_col:
            st.title("Create your student profile")
            st.caption(
                "A few quick steps to set up your secure FaceID student account."
            )
        with back_col:
            if st.button(
                "Back to login",
                icon=":material/arrow_back:",
                key="student_register_back",
                width="stretch",
                type="secondary",
            ):
                st.session_state["show_registration"] = False
                st.rerun()

    st.progress(0.15, text="Step 1 of 3 · Your details")
    with st.container(border=True):
        st.subheader("Your details")
        st.caption("Use your official name and enrollment number.")
        name_col, enrollment_col = st.columns(2)
        with name_col:
            name = st.text_input(
                "Full name",
                key="student_register_name",
                placeholder="e.g. Arjun Rajput",
            )
        with enrollment_col:
            enrollment_number = st.text_input(
                "Enrollment number",
                key="student_register_enrollment",
                placeholder="e.g. 2402309001",
            )

    st.progress(0.5, text="Step 2 of 3 · Face photos")
    with st.container(border=True):
        st.subheader("Capture your live photo")
        st.caption(
            "Look directly at the camera in good lighting. Keep only your face in frame."
        )
        photo = st.camera_input("Live photo for FaceID", key="student_register_photo")

    photos_embeddings = {}
    with st.container(border=True):
        st.subheader("Add three profile photos")
        st.caption(
            "Upload exactly three clear photos. Each photo must contain one face."
        )
        image_saving()
        photos = st.session_state.save_img
        st.badge(
            f"{len(photos)} of 3 photos added",
            icon=":material/photo_library:",
            color="green" if len(photos) == 3 else "blue",
        )

    photo_validation_error = None
    if photos:
        with st.container(border=True):
            st.write("Photo preview")
            photo_columns = st.columns(min(len(photos), 3))
            for index, uploaded_photo in enumerate(photos):
                with photo_columns[index % len(photo_columns)]:
                    st.image(
                        cv2.cvtColor(uploaded_photo, cv2.COLOR_BGR2RGB),
                        caption=f"Photo {index + 1}",
                        width="stretch",
                    )

            if st.button(
                "Remove uploaded photos",
                width="stretch",
                icon=":material/delete:",
                type="secondary",
                key="student_register_clear_photos",
            ):
                st.session_state.save_img = []
                st.session_state.photo_upload_version += 1
                st.rerun()

        if len(photos) != 3:
            st.warning("Add exactly three photos to continue.")

    for n, uploaded_photo in enumerate(photos):
        embeddings = get_face_embeddings(
            cv2.cvtColor(uploaded_photo, cv2.COLOR_BGR2RGB)
        )
        if len(embeddings) != 1:
            photo_validation_error = (
                f"Photo {n + 1} must contain exactly one face; found {len(embeddings)}."
            )
            break
        photos_embeddings[f"face_embedding{n + 2}"] = [
            embedding.tolist() for embedding in embeddings
        ]

    with st.container(border=True):
        st.subheader("VoiceID (optional)")
        st.caption("You can add a voice sample now or continue without VoiceID.")
        audio_data = st.audio_input(
            "Record a short voice sample", key="student_register_audio"
        )

    st.progress(
        1.0 if name and enrollment_number and photo and len(photos) == 3 else 0.8,
        text="Step 3 of 3 · Review and create your account",
    )
    with st.container(border=True):
        st.caption(
            "By creating your profile, your face photos are used to set up student recognition."
        )
        submit_col, _ = st.columns([1, 2])
        with submit_col:
            submit_registration = st.button(
                "Create student account",
                key="student_register_submit",
                icon=":material/person_add:",
                type="primary",
                width="stretch",
            )

    if submit_registration:
        if not name or not enrollment_number or not photo:
            st.warning(
                "Please enter your name and enrollment number and capture a live photo."
            )
            return
        if len(photos) != 3:
            st.warning("Please upload exactly 3 student photos.")
            return
        if photo_validation_error:
            st.warning(photo_validation_error)
            return

        try:
            img = np.array(Image.open(photo))
            face_embeddings = get_face_embeddings(img)
            if len(face_embeddings) != 1:
                st.warning(
                    "The live photo must contain exactly one face; "
                    f"found {len(face_embeddings)}."
                )
                return
            audio_embedding = None
            if audio_data:
                audio_embedding = voice_embedding(audio_data)
                if audio_embedding is None:
                    st.warning(
                        "Voice embedding could not be generated. "
                        "voice again or remove the recording to continue without VoiceID."
                    )
                    return

            student = create_student(
                name,
                enrollment_number,
                face_embeddings,
                photos_embeddings["face_embedding2"],
                photos_embeddings["face_embedding3"],
                photos_embeddings["face_embedding4"],
                audio_embedding,
            )
            if student:
                st.success("Registration Successfull!")
                st.session_state["show_registration"] = False
                st.session_state["login_type"] = "Student"
                st.rerun()

            else:
                st.error(
                    "Registration could not be saved. Check the Supabase connection "
                    "and student table, then try again."
                )
        except ConnectionError:
            st.error(
                "Could not connect to Supabase to save your registration. "
                "Check your internet connection and Supabase project status, "
                "then submit again."
            )
        except Exception as e:
            st.error(f"An error occurred during registration: {e}")


home_footer()


def delete_button(subject_id):
    if st.button(
        "",
        icon=":material/delete:",
        type="secondary",
        key=f"delete_subject{subject_id}",
    ):
        confirm_enrollment_deletion(
            subject_id, st.session_state.student_data.get("student_id")
        )


def student_dashboard():
    student_data = _get_student_session_data()
    if student_data is None:
        st.error("Your student session is missing a student ID. Please log in again.")
        return
    student_id = student_data["student_id"]
    col1, col2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    h_col1, h_col2 = st.columns(2, gap="large")
    with col2:
        header_dashboard()
    with col1:
        st.header("Your Enrolled Subjects", text_alignment="center")
    with h_col2:
        if st.button(
            "Back to Home✈", type="secondary", key="btt1", shortcut="control+backspace"
        ):
            st.session_state["login_type"] = None
            st.session_state.is_logged_in = False
            st.session_state.user_role = None
            st.session_state.user_data = None
            st.session_state.student_data = None
            st.rerun()
    with h_col1:
        if st.button(
            "Enroll Subject", type="secondary", width="stretch", key="enroll_subject"
        ):
            subject_enrollment(student_id)
    st.divider()
    with st.spinner("Fetching your subjects..."):
        subjects = get_student_subjects(student_id)
        attendance_data = get_student_attendance(student_id)
    states_map = {}
    for log in attendance_data:
        subject_id = log.get("subject_id")
        if subject_id not in states_map:
            states_map[subject_id] = {"present": 0, "absent": 0}
        if log.get("is_present"):
            states_map[subject_id]["present"] += 1
        else:
            states_map[subject_id]["absent"] += 1
    col = st.columns(2, gap="small")
    for i, sub_nodes in enumerate(subjects):
        with col[i % 2]:
            subject_id = sub_nodes.get("subject_id")
            subject = sub_nodes.get("subjects") or {}
            present_count = states_map.get(subject_id, {}).get("present", 0)
            absent_count = states_map.get(subject_id, {}).get("absent", 0)
            subject_card(
                subject_name=subject.get("name"),
                subject_code=subject.get("subject_code"),
                program=subject.get("Program"),
                section=subject.get("section"),
                stats=[
                    ("✅", "Present", present_count),
                    ("✖️", "Absent", absent_count),
                ],
            )
            delete_button(subject_id)
