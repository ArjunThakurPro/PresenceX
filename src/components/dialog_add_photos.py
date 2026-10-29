import streamlit as st
from src.database.config import supabase
from PIL import Image
from src.pipelines.face_pipeline import predict_attendence
import time


@st.dialog("Capture or Upload a photo")
def add_photo_dialog():
    st.write("Take Photos for Attendance Marking")
    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "Camera"
    t1, t2 = st.columns(2)
    with t1:
        type_camera = (
            "primary" if st.session_state.photo_tab == "Camera" else "secondary"
        )
        if st.button(
            "Camera", type=type_camera, width="stretch", icon=":material/camera:"
        ):
            st.session_state.photo_tab = "Camera"
    with t2:
        type_upload = (
            "primary" if st.session_state.photo_tab == "upload" else "secondary"
        )
        if st.button("Upload_images", type=type_upload, width="stretch"):
            st.session_state.photo_tab = "upload"
    if st.session_state.photo_tab == "Camera":
        st.caption("Capture a class photo to identify students and record attendance.")
        faces = st.camera_input("Take a picture of the class to mark attendance")
        if faces:
            st.session_state.attendance_image.append(Image.open(faces))
            st.toast("photo captured")
        if faces:
            detected_student, _, _ = predict_attendence(faces)
            if detected_student:
                student_ids = [str(student_id) for student_id in detected_student]
                st.success(
                    f"Attendance marked for {len(detected_student)} students: {', '.join(student_ids)}"
                )
                time.sleep(3)
                st.rerun()

            else:
                st.warning("No students detected in the image.")
                st.rerun()
            st.info("This feature is under development. Please check back later.")
    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader(
            "Choose Image files",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="file_uploading",
        )
        if uploaded_files:
            for img in uploaded_files:
                st.session_state.attendance_image.append(Image.open(img))
            st.toast("photos Uploaded Successfully")
            st.rerun()
    st.divider()
    if st.button("Done", width="content"):
        st.rerun()
