import io

import dlib
import face_recognition_models
import numpy as np
import streamlit as st
from PIL import Image

from src.database.db import get_all_students


def _to_numpy_image(img):
    if img is None:
        return None
    if isinstance(img, np.ndarray):
        return img
    if isinstance(img, Image.Image):
        return np.array(img.convert("RGB"))
    if hasattr(img, "getvalue"):
        with Image.open(io.BytesIO(img.getvalue())) as pil_image:
            return np.array(pil_image.convert("RGB"))
    if isinstance(img, (bytes, bytearray)):
        with Image.open(io.BytesIO(img)) as pil_image:
            return np.array(pil_image.convert("RGB"))
    if hasattr(img, "read"):
        data = img.read()
        if isinstance(data, (bytes, bytearray)):
            with Image.open(io.BytesIO(data)) as pil_image:
                return np.array(pil_image.convert("RGB"))
    return np.asarray(img)


@st.cache_resource  # it prevent to load data reapitly
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    landmark_model = face_recognition_models.pose_predictor_model_location()
    sp = dlib.shape_predictor(landmark_model)
    face_rec_model = face_recognition_models.face_recognition_model_location()
    face_rec = dlib.face_recognition_model_v1(face_rec_model)
    return detector, sp, face_rec


def get_face_embeddings(img_np):
    img_np = _to_numpy_image(img_np)
    detector, sp, face_rec = load_dlib_models()
    faces = detector(img_np, 1)
    encodings = []
    for face in faces:
        landmarks = sp(img_np, face)
        face_descriptor = face_rec.compute_face_descriptor(
            img_np, landmarks, 1
        )  # 128 Embeddings
        encodings.append(np.array(face_descriptor))
    return encodings


def train_model():
    x_train = []
    y_train = []
    students_db = get_all_students()
    if not students_db:
        return None

    for student in students_db:
        student_id = student.get("student_id")
        if student_id is None:
            continue

        for field in (
            "face_embedding",
            "face_embedding2",
            "face_embedding3",
            "face_embedding4",
        ):
            value = student.get(field)
            if value is None:
                continue

            try:
                embedding_array = np.asarray(value, dtype=float)
            except (TypeError, ValueError):
                continue

            if embedding_array.ndim == 1:
                embedding_array = embedding_array.reshape(1, -1)
            if embedding_array.ndim != 2 or embedding_array.shape[1] != 128:
                continue

            for face_embedding in embedding_array:
                if np.all(np.isfinite(face_embedding)):
                    x_train.append(face_embedding)
                    y_train.append(student_id)

    if not x_train:
        return None

    return {"X": x_train, "Y": y_train}


def train_classifier():
    model_data = train_model()
    return bool(model_data)


def predict_attendence(class_img):

    embeddings = get_face_embeddings(class_img)
    detected_student = {}
    model_data = train_model()
    if not model_data or not embeddings:
        return detected_student, [], len(embeddings)

    x_train = np.asarray(model_data["X"], dtype=float)
    y_train = model_data["Y"]
    all_students = list(dict.fromkeys(y_train))

    for encoding in embeddings:
        encoding = np.asarray(encoding, dtype=float)
        if encoding.shape != (128,) or not np.all(np.isfinite(encoding)):
            continue

        distances = np.linalg.norm(x_train - encoding, axis=1)
        best_match_index = int(np.argmin(distances))
        best_match_score = float(distances[best_match_index])
        predicted_id = y_train[best_match_index]
        resemblance_threshold = 0.5
        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(embeddings)
