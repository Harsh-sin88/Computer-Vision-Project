"""
Module: enrollment  (Functional Module 1 — Student Enrollment)
Handles registering a new student: storing their metadata and capturing
labelled face samples that the recognizer will later be trained on.

Two capture paths are supported:
  - capture_from_webcam(): local laptop/USB camera, used by scripts/enroll_cli.py
  - save_uploaded_sample(): image bytes uploaded through the web API

Training is decoupled into train_recognizer() so it can be re-run any time
new students or new samples are added, without touching enrollment logic.
"""
import json
import os

import cv2
import numpy as np

from app import config, face_utils, database


def _next_label_id(conn) -> int:
    students = database.list_students(conn)
    return max((s.label_id for s in students), default=0) + 1


def register_student(conn, name: str, roll_number: str) -> int:
    """Create the DB row for a new student and their sample folder. Returns label_id."""
    label_id = _next_label_id(conn)
    database.add_student(conn, label_id, name, roll_number)
    student_dir = os.path.join(config.FACES_DIR, str(label_id))
    os.makedirs(student_dir, exist_ok=True)
    return label_id


def save_face_sample(label_id: int, face_image: np.ndarray) -> str:
    """Persist one preprocessed face crop to disk under the student's folder."""
    student_dir = os.path.join(config.FACES_DIR, str(label_id))
    os.makedirs(student_dir, exist_ok=True)
    existing = len(os.listdir(student_dir))
    path = os.path.join(student_dir, f"{existing + 1}.png")
    cv2.imwrite(path, face_image)
    return path


def save_uploaded_sample(label_id: int, image_bytes: bytes) -> dict:
    """Decode an uploaded image, extract the face, and save it as a sample."""
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        return {"saved": False, "reason": "invalid_image"}
    face, box = face_utils.extract_largest_face(frame)
    if face is None:
        return {"saved": False, "reason": "no_face_detected"}
    path = save_face_sample(label_id, face)
    return {"saved": True, "path": path, "box": list(map(int, box))}


def capture_from_webcam(label_id: int, num_samples: int = None, camera_index: int = 0) -> int:
    """
    CLI-only helper: opens a local webcam, collects `num_samples` face crops
    for the given label, saving each one to disk. Not used by the web API,
    which has no direct camera access on the server.
    """
    num_samples = num_samples or config.SAMPLES_PER_STUDENT
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    collected = 0
    try:
        while collected < num_samples:
            ok, frame = cap.read()
            if not ok:
                continue
            face, box = face_utils.extract_largest_face(frame)
            if face is not None:
                save_face_sample(label_id, face)
                collected += 1
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Samples: {collected}/{num_samples}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Enrollment - press q to stop", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return collected


def train_recognizer() -> dict:
    """
    Train an LBPH face recognizer on every saved sample across all students
    and persist the model + label map to disk. Must be re-run after enrolling
    new students or new samples, before recognition will pick them up.
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    images, labels = [], []
    labels_map = {}

    for label_dir in sorted(os.listdir(config.FACES_DIR)):
        full_dir = os.path.join(config.FACES_DIR, label_dir)
        if not os.path.isdir(full_dir) or not label_dir.isdigit():
            continue
        label_id = int(label_dir)
        for fname in os.listdir(full_dir):
            img = cv2.imread(os.path.join(full_dir, fname), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(label_id)
        if any(l == label_id for l in labels):
            labels_map[label_id] = label_dir

    if not images:
        raise RuntimeError("No face samples found. Enroll at least one student first.")

    recognizer.train(images, np.array(labels))
    recognizer.write(config.MODEL_PATH)
    with open(config.LABELS_PATH, "w") as f:
        json.dump(labels_map, f)

    return {"students_trained": len(labels_map), "total_samples": len(images)}
