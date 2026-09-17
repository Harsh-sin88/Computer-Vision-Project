"""
Module: face_utils
Shared low-level image processing utilities for face detection and
preprocessing. Implements concepts from Syllabus Module 1 (image formation &
low-level processing) and Module 3 (feature extraction) of CSE3010 Computer
Vision: grayscale conversion, Haar-cascade based detection, and histogram
equalization for illumination normalization.
"""
import os

import cv2
import numpy as np

from app import config

_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
_face_cascade = None


def get_cascade():
    """Lazily load the Haar cascade classifier used for face detection."""
    global _face_cascade
    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
        if _face_cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade from {_CASCADE_PATH}")
    return _face_cascade


def to_gray(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to single-channel grayscale (pass-through if already gray)."""
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def detect_faces(gray_image: np.ndarray):
    """
    Detect faces in a grayscale image using a Haar cascade classifier.
    Returns a list of (x, y, w, h) bounding boxes.
    """
    cascade = get_cascade()
    faces = cascade.detectMultiScale(
        gray_image,
        scaleFactor=config.DETECTION_SCALE_FACTOR,
        minNeighbors=config.DETECTION_MIN_NEIGHBORS,
        minSize=(60, 60),
    )
    return list(faces)


def crop_and_resize(gray_image: np.ndarray, box) -> np.ndarray:
    """Crop a face region from a grayscale image and resize it to a fixed size."""
    x, y, w, h = box
    face = gray_image[y:y + h, x:x + w]
    return cv2.resize(face, config.FACE_SIZE)


def preprocess_face(face_image: np.ndarray) -> np.ndarray:
    """
    Normalize illumination via histogram equalization. Improves robustness of
    LBPH recognition to lighting changes between enrollment and recognition.
    """
    return cv2.equalizeHist(face_image)


def extract_largest_face(image: np.ndarray):
    """
    Convenience helper: given a raw BGR frame, return the preprocessed crop of
    the largest detected face plus its bounding box, or (None, None) if no
    face is found. Used by both enrollment and recognition so the two stages
    always see faces prepared the same way.
    """
    gray = to_gray(image)
    faces = detect_faces(gray)
    if not faces:
        return None, None
    largest = max(faces, key=lambda b: b[2] * b[3])
    face_crop = crop_and_resize(gray, largest)
    return preprocess_face(face_crop), largest
