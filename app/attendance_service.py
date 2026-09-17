"""
Module: attendance_service
Business logic sitting between face recognition and storage: decides whether
a recognized face is confident enough to be marked present, and computes the
daily summary used by the dashboard and reports.
"""
from datetime import datetime

from app import config, database


def mark_if_confident(conn, label_id: int, confidence: float) -> dict:
    """
    LBPH confidence is a *distance* — lower means a closer match. Only mark
    attendance if the distance is below the configured threshold, otherwise
    treat the face as unrecognized rather than risk a false positive.
    """
    if confidence > config.RECOGNITION_CONFIDENCE_THRESHOLD:
        return {"recognized": False, "reason": "confidence_too_low", "confidence": confidence}

    student = database.get_student_by_label(conn, label_id)
    if student is None:
        return {"recognized": False, "reason": "unknown_label"}

    inserted = database.mark_attendance(conn, student.id, confidence)
    return {
        "recognized": True,
        "student": {"name": student.name, "roll_number": student.roll_number},
        "confidence": confidence,
        "attendance_marked": inserted,
        "already_marked_today": not inserted,
    }


def todays_summary(conn) -> dict:
    today = datetime.now().date().isoformat()
    present = database.get_attendance_for_date(conn, today)
    total_students = len(database.list_students(conn))
    present_count = len(present)
    percentage = round((present_count / total_students) * 100, 1) if total_students else 0.0
    return {
        "date": today,
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": total_students - present_count,
        "attendance_percentage": percentage,
        "present": present,
    }
