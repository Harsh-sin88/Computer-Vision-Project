"""
Module: recognition (Functional Module 2 — Recognition & Attendance Marking)
Loads the trained LBPH model and matches new face crops against it. Also
provides a CLI live-recognition loop that marks attendance directly, for use
with scripts/recognize_cli.py.
"""
import os

import cv2
import numpy as np

from app import config, face_utils, database
from app.attendance_service import mark_if_confident

_recognizer = None


def _ensure_model_exists():
    if not os.path.exists(config.MODEL_PATH):
        raise RuntimeError("No trained model found. Run enrollment.train_recognizer() first.")


def load_recognizer():
    global _recognizer
    if _recognizer is None:
        _ensure_model_exists()
        _recognizer = cv2.face.LBPHFaceRecognizer_create()
        _recognizer.read(config.MODEL_PATH)
    return _recognizer


def reload_recognizer():
    """Force a reload from disk — call after re-training so the new model takes effect."""
    global _recognizer
    _recognizer = None
    return load_recognizer()


def recognize_face(face_image: np.ndarray):
    """Return (label_id, confidence) for a single preprocessed face crop.
    Confidence is an LBPH distance: lower means a closer match."""
    recognizer = load_recognizer()
    label_id, confidence = recognizer.predict(face_image)
    return label_id, confidence


def recognize_from_bytes(image_bytes: bytes) -> dict:
    """Full pipeline: raw uploaded image bytes -> detection -> recognition ->
    attendance decision. Used by the /attendance/recognize API endpoint."""
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        return {"recognized": False, "reason": "invalid_image"}

    face, box = face_utils.extract_largest_face(frame)
    if face is None:
        return {"recognized": False, "reason": "no_face_detected"}

    label_id, confidence = recognize_face(face)
    conn = database.get_connection()
    try:
        result = mark_if_confident(conn, label_id, confidence)
    finally:
        conn.close()
    result["box"] = list(map(int, box))
    return result


def run_live_recognition(camera_index: int = 0):
    """
    CLI-only helper: continuously reads webcam frames, recognizes faces, and
    marks attendance in real time. Intended for scripts/recognize_cli.py.
    """
    conn = database.get_connection()
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            gray = face_utils.to_gray(frame)
            for box in face_utils.detect_faces(gray):
                face = face_utils.preprocess_face(face_utils.crop_and_resize(gray, box))
                label_id, confidence = recognize_face(face)
                result = mark_if_confident(conn, label_id, confidence)
                x, y, w, h = box
                if result.get("recognized"):
                    text = result["student"]["name"]
                    color = (0, 255, 0)
                else:
                    text = "Unknown"
                    color = (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow("Attendance - press q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        conn.close()
