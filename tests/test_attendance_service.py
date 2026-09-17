import pytest

from app import database, config
from app.attendance_service import mark_if_confident, todays_summary


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    connection = database.get_connection(str(db_path))
    yield connection
    connection.close()


def test_add_and_fetch_student(conn):
    database.add_student(conn, label_id=1, name="Alice", roll_number="R001")
    student = database.get_student_by_label(conn, 1)
    assert student.name == "Alice"
    assert student.roll_number == "R001"


def test_mark_attendance_once_per_day(conn):
    student_id = database.add_student(conn, label_id=1, name="Alice", roll_number="R001")
    first = database.mark_attendance(conn, student_id, confidence=40.0)
    second = database.mark_attendance(conn, student_id, confidence=38.0)
    assert first is True
    assert second is False  # duplicate mark for the same day is rejected


def test_mark_if_confident_rejects_low_confidence_match(conn):
    database.add_student(conn, label_id=1, name="Alice", roll_number="R001")
    result = mark_if_confident(conn, label_id=1, confidence=config.RECOGNITION_CONFIDENCE_THRESHOLD + 5)
    assert result["recognized"] is False
    assert result["reason"] == "confidence_too_low"


def test_mark_if_confident_marks_known_student(conn):
    database.add_student(conn, label_id=1, name="Alice", roll_number="R001")
    result = mark_if_confident(conn, label_id=1, confidence=30.0)
    assert result["recognized"] is True
    assert result["attendance_marked"] is True


def test_mark_if_confident_unknown_label(conn):
    result = mark_if_confident(conn, label_id=99, confidence=10.0)
    assert result["recognized"] is False
    assert result["reason"] == "unknown_label"


def test_todays_summary_counts_present_and_absent(conn):
    database.add_student(conn, label_id=1, name="Alice", roll_number="R001")
    database.add_student(conn, label_id=2, name="Bob", roll_number="R002")
    mark_if_confident(conn, label_id=1, confidence=30.0)

    summary = todays_summary(conn)
    assert summary["total_students"] == 2
    assert summary["present_count"] == 1
    assert summary["absent_count"] == 1
