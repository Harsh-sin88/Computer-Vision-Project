"""
Module: config
Central place for paths and tunable parameters used across the system.
Keeping these in one file makes the non-functional "maintainability" and
"resource efficiency" requirements easy to demonstrate and adjust.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "faces")
MODEL_PATH = os.path.join(DATA_DIR, "lbph_model.yml")
LABELS_PATH = os.path.join(DATA_DIR, "labels.json")
DB_PATH = os.path.join(DATA_DIR, "attendance.db")

# Face detection / preprocessing
FACE_SIZE = (200, 200)
DETECTION_SCALE_FACTOR = 1.1
DETECTION_MIN_NEIGHBORS = 5

# Recognition
# LBPH confidence is a DISTANCE (lower = better match). Anything above this
# threshold is treated as "not confident enough" and attendance is not marked.
RECOGNITION_CONFIDENCE_THRESHOLD = 70.0

# Enrollment
SAMPLES_PER_STUDENT = 25

os.makedirs(FACES_DIR, exist_ok=True)
