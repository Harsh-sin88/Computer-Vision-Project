import numpy as np

from app import face_utils, config


def test_to_gray_passthrough_for_single_channel():
    gray = np.zeros((50, 50), dtype=np.uint8)
    assert face_utils.to_gray(gray) is gray


def test_to_gray_converts_bgr():
    bgr = np.zeros((50, 50, 3), dtype=np.uint8)
    result = face_utils.to_gray(bgr)
    assert result.ndim == 2
    assert result.shape == (50, 50)


def test_crop_and_resize_returns_configured_face_size():
    gray = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
    box = (10, 10, 80, 80)
    face = face_utils.crop_and_resize(gray, box)
    assert face.shape == config.FACE_SIZE


def test_preprocess_face_returns_same_shape_and_dtype():
    face = np.random.randint(0, 255, config.FACE_SIZE, dtype=np.uint8)
    result = face_utils.preprocess_face(face)
    assert result.shape == face.shape
    assert result.dtype == face.dtype


def test_detect_faces_on_blank_image_returns_empty_list():
    blank = np.zeros((300, 300), dtype=np.uint8)
    assert face_utils.detect_faces(blank) == []


def test_extract_largest_face_on_blank_image_returns_none():
    blank = np.zeros((300, 300, 3), dtype=np.uint8)
    face, box = face_utils.extract_largest_face(blank)
    assert face is None
    assert box is None
