import streamlit as st
import cv2
import numpy as np
from PIL import Image
from src.database.config import supabase
from src.pipelines.face_pipeline import get_face_embeddings
import time


def image_saving():
    if "save_img" not in st.session_state:
        st.session_state.save_img = []
    if "photo_upload_version" not in st.session_state:
        st.session_state.photo_upload_version = 0

    upload = st.file_uploader(
        "Choose Image files",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"file_uploading_{st.session_state.photo_upload_version}",
    )

    photos = []
    for n, img in enumerate(upload):
        try:
            with Image.open(img) as uploaded_photo:
                rgb_image = np.array(uploaded_photo.convert("RGB"))
        except OSError:
            st.error(f"Photo {n + 1} is not a valid image.")
            st.session_state.save_img = []
            return None

        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        sharpened_photo = improve_face_image(bgr_image)
        photos.append(sharpened_photo)

    st.session_state.save_img = photos


def improve_face_image(image):
    if image is None or image.size == 0:
        raise ValueError("Invalid or empty image")

    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab_image)

    blurred = cv2.GaussianBlur(lightness, (0, 0), sigmaX=1.0)
    sharpened_lightness = cv2.addWeighted(
        lightness, 1.7, blurred, -0.7, 0
    )

    sharpened_lab = cv2.merge((sharpened_lightness, a_channel, b_channel))
    return cv2.cvtColor(sharpened_lab, cv2.COLOR_LAB2BGR)
